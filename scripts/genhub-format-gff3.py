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
import re
import sys


def parse_args():
    sources = ['ncbi', 'ncbi_flybase', 'beebase', 'crg', 'pdom']
    desc = 'Filter features and parse accession values'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('-p', '--prefix', default=None,
                        help='attach the given prefix to each sequence ID')
    parser.add_argument('-s', '--source', default='ncbi', choices=sources,
                        help='data source; default is "ncbi"')
    parser.add_argument('gff3', type=argparse.FileType('r'))
    return parser.parse_args()


def match_filter(line, source):
    if source in ['ncbi', 'ncbi_flybase']:
        for filt in ['\tregion\t', '\tmatch\t', '\tcDNA_match\t', '##species']:
            if filt in line:
                return True
    return False


def parse_gene_accession(line, source):
    if '\tgene\t' not in line or source == 'beebase':
        return line

    accmatch = None
    if source in ['ncbi', 'ncbi_flybase']:
        accmatch = re.search('GeneID:([^;,\n]+)', line)
    elif source == 'crg':
        accmatch = re.search('ID=([^;\n]+)', line)
    elif source == 'pdom':
        accmatch = re.search('Name=([^;\n]+)', line)
    else:
        pass
    assert accmatch, 'unable to parse gene accession: %s' % line
    return line + ';accession=' + accmatch.group(1)


def parse_transcript_accession(line, source, rnaid_to_accession):
    fields = line.split('\t')
    if len(fields) != 9:
        return line

    ftype = fields[2]
    if ftype not in ['mRNA', 'tRNA', 'rRNA', 'ncRNA', 'transcript',
                     'primary_transcript']:
        return line

    accmatch = None
    idmatch = None
    if source in ['ncbi', 'ncbi_flybase']:
        accmatch = re.search('transcript_id=([^;\n]+)', line)
        idmatch = re.search('GeneID:([^;,\n]+)', line)
    elif source == 'crg':
        accmatch = re.search('ID=([^;\n]+)', line)
    elif source == 'pdom':
        accmatch = re.search('ID=([^;\n]+)', line)
    elif source == 'beebase':
        accmatch = re.search('Name=([^;\n]+)', line)
    else:
        pass
    assert accmatch or idmatch, \
        'unable to parse transcript accession: %s' % line
    if accmatch:
        accession = accmatch.group(1)
    else:
        accession = '%s:%s' % (idmatch.group(1), ftype)
    line += ';accession=' + accession
    rnaid = re.search('ID=([^;\n]+)', line).group(1)
    rnaid_to_accession[rnaid] = accession
    return line


def parse_transcript_feature_accession(line, source, rnaid_to_accession):
    fields = line.split('\t')
    if len(fields) != 9:
        return line

    ftype = fields[2]
    if ftype not in ['exon', 'intron', 'CDS']:
        return line

    rnaid = re.search('Parent=([^;\n]+)', line).group(1)
    assert ',' not in rnaid, rnaid
    assert rnaid in rnaid_to_accession, rnaid
    return line + ';accession=' + rnaid_to_accession[rnaid]


def format_prefix(line, prefix):
    if len(line.split('\t')) == 9:
        return prefix + line
    elif line.startswith('##sequence-region'):
        return re.sub('##sequence-region(\s+)(\S+)',
                      '##sequence-region\g<1>%s\g<2>' % args.prefix, line)


def format_gff3(instream, source, prefix=None):
    id2acc = dict()
    for line in args.gff3:
        line = line.rstrip()
        if match_filter(line, source):
            continue

        line = parse_gene_accession(line, source)
        line = parse_transcript_accession(line, source, id2acc)
        line = parse_transcript_feature_accession(line, source, id2acc)
        if args.prefix:
            line = process_prefix(line, args.prefix)

        yield line


if __name__ == '__main__':
    args = parse_args()
    for line in format_gff3(args.gff3, args.source):
        print(line, file=args.outfile)
