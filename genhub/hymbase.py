#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2017   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2017   Regents of the University of California.
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""
Retrieve and format data from BeeBase.

GenomeDB implementation for BeeBase consortium data provisioned by
HymenopteraBase.
"""

from __future__ import print_function
import filecmp
import gzip
import re
import subprocess
import sys
import genhub


class HymBaseDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(HymBaseDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'hymbase'
        genus = self.config['species'].split()[0].lower()
        self.specbase = 'http://hymenopteragenome.org/drupal/sites/'
        self.specbase += 'hymenopteragenome.org.%s/files/data' % genus

    def __repr__(self):
        return 'HymenopteraBase'

    @property
    def gdnaurl(self):
        return '%s/%s' % (self.specbase, self.gdnafilename)

    @property
    def gff3url(self):
        return '%s/%s' % (self.specbase, self.gff3filename)

    @property
    def proturl(self):
        return '%s/%s' % (self.specbase, self.protfilename)

    def format_gdna(self, instream, outstream, logstream=sys.stderr):
        self.format_fasta(instream, outstream, logstream)

    def format_prot(self, instream, outstream, logstream=sys.stderr):
        self.format_fasta(instream, outstream, logstream)

    def format_fasta(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.startswith('>gnl|'):
                deflinematch = re.search('>gnl\|[^\|]+\|(\S+)', line)
                assert deflinematch, line
                protid = deflinematch.group(1)
                line = line.replace('>', '>%s ' % protid)
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('gunzip -c %s' % self.gff3path)
        if 'annotfilter' in self.config:
            excludefile = self.filter_file()
            cmds.append('grep -vf %s' % excludefile.name)
        cmds.append('grep -v "\tregion\t"')
        cmds.append('genhub-namedup.py')
        cmds.append('tidygff3')
        cmds.append('genhub-format-gff3.py --source beebase -')
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
            protid = namematch.group(1).replace('-RA', '-PA')
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
                protid = idmatch.group(2).replace('-RA', '-PA')
                geneid = idmatch.group(1)
                locusid = gene2loci[geneid]
                locusname = locusid2name[locusid]
                yield protid, locusname


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds_download():
    """HymBase: scaffolds download"""
    cfdb = genhub.test_registry.genome('Cfhb')
    testurl = ('http://hymenopteragenome.org/drupal/sites/hymenopteragenome.'
               'org.camponotus/files/data/Cflo_3.3_scaffolds.fa.gz')
    testpath = './Cfhb/Cflo_3.3_scaffolds.fa.gz'
    assert cfdb.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (cfdb.gdnaurl, testurl)
    assert cfdb.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (cfdb.gdnapath, testpath)
    assert '%r' % cfdb == 'HymenopteraBase'
