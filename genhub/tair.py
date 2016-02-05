#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""
Retrieve and format data from The Arabidopsis Information Resource.

GenomeDB implementation for data residing in TAIR. Currently tested only on
TAIR6, but presumably trivial to extend to other versions using Att6.yml as a
template.
"""

from __future__ import print_function
import filecmp
import gzip
import os
import re
import subprocess
import sys
import genhub


class TairDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(TairDB, self).__init__(label, conf, workdir)

        assert self.config['source'] == 'tair'
        assert 'version' in self.config
        assert str(self.config['version']) == '6'
        assert 'species' in self.config
        assert self.config['species'] == 'Arabidopsis thaliana'

        self.specbase = 'ftp://ftp.arabidopsis.org/home/tair'
        self.format_gdna = self.format_fasta
        self.format_prot = self.format_fasta

    def __repr__(self):
        return 'TAIR' + self.version

    @property
    def version(self):
        return str(self.config['version'])

    @property
    def gdnafilename(self):
        return self.config['gdna_filename']

    @property
    def gff3filename(self):
        return self.config['gff3_filename']

    @property
    def protfilename(self):
        return self.config['prot_filename']

    @property
    def gdnaurl(self):
        return self.config['gdna_url']

    @property
    def gff3url(self):
        return self.config['gff3_url']

    @property
    def proturl(self):
        return self.config['prot_url']

    def format_fasta(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            # No processing required.
            # If any is ever needed again, do it here.
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('gunzip -c %s' % self.gff3path)
        if 'annotfilter' in self.config:
            excludefile = self.filter_file()
            cmds.append('grep -vf %s' % excludefile.name)
        cmds.append('sed "s/Index=/index=/"')
        cmds.append('tidygff3')
        cmds.append('genhub-format-gff3.py --source tair -')
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
               'more than one pseudogene attribute' not in line and \
               line != '':
                print(line, file=logstream)
        assert proc.returncode == 0, \
            'annot cleanup command failed: %s' % commands
        if 'annotfilter' in self.config:
            os.unlink(excludefile.name)

    def gff3_protids(self, instream):
        protids = dict()
        for line in instream:
            if '\tmRNA\t' not in line:
                continue
            idmatch = re.search('Name=([^;\n]+)', line)
            assert idmatch, 'cannot parse protein ID: ' + line
            protid = idmatch.group(1)
            assert protid not in protids, protid
            protids[protid] = True
            yield protid

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
                if idmatch:
                    geneid = idmatch.group(1)
                    ilocusid = idmatch.group(2)
                    gene2loci[geneid] = ilocusid
                else:  # pragma: no cover
                    print('Unable to parse gene and iLocus IDs: %s' % attrs,
                          file=sys.stderr)
            elif feattype == 'mRNA':
                idmatch = re.search('Parent=([^;\n]+);Name=([^;\n]+)', attrs)
                assert idmatch, \
                    'Unable to parse mRNA and gene IDs: %s' % attrs.rstrip()
                geneid = idmatch.group(1)
                mrnaid = idmatch.group(2)
                ilocusid = gene2loci[geneid]
                ilocusname = locusid2name[ilocusid]
                yield mrnaid, ilocusname


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------
