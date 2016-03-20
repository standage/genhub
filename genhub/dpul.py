#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Genome database implementation for *Daphnia pulex* genome data."""

from __future__ import print_function
import filecmp
import gzip
import re
import subprocess
import sys
import genhub


class DpulDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(DpulDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'dpul'

    def __repr__(self):
        return 'DpulDB'

    def format_gdna(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            # No processing required currently.
            # If any is ever needed, do it here.
            print(line, end='', file=outstream)

    def format_prot(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.strip() == '':
                continue
            if line.startswith('>'):
                if line.strip().endswith('|'):
                    line = line[:-2] + '\n'
                protid = line.split('|')[-1]
                line = '>' + protid
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('tidygff3 < %s' % self.gff3path)
        cmds.append('genhub-format-gff3.py --source pdom -')
        cmds.append('seq-reg.py - %s' % self.gdnafile)
        cmds.append('gt gff3 -sort -tidy -o %s -force' % self.gff3file)

        commands = ' | '.join(cmds)
        if debug:  # pragma: no cover
            print('DEBUG: running command: %s' % commands, file=logstream)
        proc = subprocess.Popen(commands, shell=True, universal_newlines=True,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        for line in stderr.split('\n'):  # pragma: no cover
            if 'has not been previously introduced' not in line and \
               'does not begin with "##gff-version"' not in line and \
               'illegal uppercase attribute "Shift"' not in line and \
               'has the wrong phase' not in line and \
               line != '':
                print(line, file=logstream)
        assert proc.returncode == 0, \
            'annot cleanup command failed: %s' % commands

    def gff3_protids(self, instream):
        for line in instream:
            if '\tmRNA\t' not in line:
                continue
            namematch = re.search('Name=([^;\n]+)', line)
            assert namematch, 'cannot parse mRNA name: ' + line
            yield namematch.group(1)

    def protein_mapping(self, instream):
        locusid2name = dict()
        gene2loci = dict()
        for line in instream:
            fields = line.split('\t')
            if len(fields) != 9:
                continue
            feattype = fields[2]
            attrs = fields[8]

            if feattype == 'locus':
                idmatch = re.search('ID=([^;\n]+);.*Name=([^;\n]+)', attrs)
                if idmatch:
                    locusid = idmatch.group(1)
                    locusname = idmatch.group(2)
                    locusid2name[locusid] = locusname
            elif feattype == 'gene':
                idmatch = re.search('ID=([^;\n]+);Parent=([^;\n]+)', attrs)
                assert idmatch, \
                    'Unable to parse gene and iLocus IDs: %s' % attrs
                geneid = idmatch.group(1)
                ilocusid = idmatch.group(2)
                gene2loci[geneid] = ilocusid
            elif feattype == 'mRNA':
                pattern = 'Parent=([^;\n]+);.*Name=([^;\n]+)'
                idmatch = re.search(pattern, attrs)
                assert idmatch, \
                    'Unable to parse mRNA and gene IDs: %s' % attrs
                protid = idmatch.group(2)
                geneid = idmatch.group(1)
                locusid = gene2loci[geneid]
                locusname = locusid2name[locusid]
                yield protid, locusname
