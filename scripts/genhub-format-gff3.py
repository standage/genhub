#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

from __future__ import print_function
import argparse
import sys
import re


if __name__ == '__main__':
    desc = 'Preliminary clean up / processing of GFF3 files'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--mode', default='ncbi', help='processing mode;'
                        ' allowed values are "ncbi" and "pdom"; default is'
                        '"ncbi"')
    parser.add_argument('gff3', type=argparse.FileType('r'), default=sys.stdin,
                        help='iLocus GFF3 file')
    args = parser.parse_args()

    rnaid_to_accession = dict()
    filterstrings = ['\tregion\t', '\tmatch\t', '\tcDNA_match\t', '##species']
    for line in args.gff3:
        line = line.rstrip()
        ignore = False
        for fs in filterstrings:
            if fs in line:
                ignore = True
                break
        if ignore:
            continue

        if '\tgene\t' in line:
            accmatch = re.search('GeneID:([^;,\n]+)', line)
            if args.mode == 'pdom':
                accmatch = re.search('Name=([^;\n]+)', line)
            assert accmatch, 'Cannot parse GeneID: %s' % line.split('\t')[-1]
            line += ';accession=%s' % accmatch.group(1)

        for rnatype in ['mRNA', 'tRNA', 'rRNA', 'ncRNA', 'transcript',
                        'primary_transcript']:
            if ('\t%s\t' % rnatype) in line:
                accmatch = re.search('transcript_id=([^;,\n]+)', line)
                if args.mode == 'pdom':
                    accmatch = re.search('ID=([^;\n]+)', line)
                if not accmatch:
                    genematch = re.search('GeneID:([^;,\n]+)', line)
                assert accmatch or genematch, \
                    'Unable to parse transcript accession: %s' % line
                if accmatch:
                    accession = accmatch.group(1)
                else:
                    rna_type = line.split('\t')[2]
                    accession = '%s:%s' % (genematch.group(1), rna_type)
                line += ';accession=%s' % accession
                rnaid = re.search('ID=([^;\n]+)', line).group(1)
                rnaid_to_accession[rnaid] = accession

        if '\texon\t' in line or '\tintron\t' in line or '\tCDS\t' in line:
            rnaid = re.search('Parent=([^;\n]+)', line).group(1)
            assert ',' not in rnaid, rnaid
            assert rnaid in rnaid_to_accession, rnaid
            if rnaid in rnaid_to_accession:
                line += ';accession=%s' % rnaid_to_accession[rnaid]

        print(line)
