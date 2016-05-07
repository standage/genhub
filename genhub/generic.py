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
GenomeDB implementation for a generic genome data set.
"""

from __future__ import print_function
import os
import re
import subprocess
import sys
import genhub


class GenericDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(GenericDB, self).__init__(label, conf, workdir)
        assert 'gdna' in self.config
        assert 'gff3' in self.config
        assert 'prot' in self.config
        assert self.config['source'] == 'local'

    @property
    def gdnapath(self):
        return self.config['gdna']

    @property
    def gff3path(self):
        return self.config['gff3']

    @property
    def protpath(self):
        return self.config['prot']

    def download(self, logstream=sys.stderr):
        if logstream is not None:
            msg = '[GenHub: %s] checking input files' % self.config['species']
            print(msg, file=logstream)
        assert os.path.isfile(self.gdnapath), \
            'gDNA file {} does not exist'.format(self.gdnapath)
        assert os.path.isfile(self.gff3path), \
            'GFF3 file {} does not exist'.format(self.gff3apath)
        assert os.path.isfile(self.protpath), \
            'proetin file {} does not exist'.format(self.protpath)

    def format_gdna(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.strip() == '':
                continue
            print(line, end='', file=outstream)

    def format_prot(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.strip() == '':
                continue
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        if self.gff3path.endswith('.gz'):
            cmds.append('gunzip -c %s' % self.gff3path)
        else:
            cmds.append('cat %s' % self.gff3path)
        cmds.append('seq-reg.py - %s' % self.gdnafile)
        cmds.append('genhub-format-gff3.py --source local -')
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
            namematch = re.search('protein_id=([^;\n]+)', line)
            if not namematch:
                namematch = re.search('Name=([^;\n]+)', line)
            assert namematch, 'cannot parse protein ID/name/accession: ' + line
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
                idmatch = re.search('Parent=([^;\n]+)', attrs)
                protmatch = re.search('protein_id=([^;\n]+)', attrs)
                if not protmatch:
                    protmatch = re.search('Name=([^;\n]+)', attrs)
                assert idmatch and protmatch, \
                    'Unable to parse protein and gene IDs: %s' % attrs
                protid = protmatch.group(1)
                geneid = idmatch.group(1)
                locusid = gene2loci[geneid]
                locusname = locusid2name[locusid]
                yield protid, locusname


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_download():
    """Pdtl figshare download"""
    config = genhub.test_registry.genome('Pdtl')
    pdom_db = PdomDB('Pdtl', config)

    assert pdom_db.gdnaurl == 'https://ndownloader.figshare.com/files/3557633'
    assert pdom_db.gff3url == 'https://ndownloader.figshare.com/files/3558071'
    assert pdom_db.proturl == 'https://ndownloader.figshare.com/files/3558059'
    assert '%r' % pdom_db == 'figshare'


def test_format():
    """Pdtl formatting task"""
    config = genhub.test_registry_supp.genome('Pdtl')
    pdom_db = PdomDB('Pdtl', config, workdir='testdata/demo-workdir')

    pdom_db.preprocess_gdna(logstream=None)
    pdom_db.preprocess_gff3(logstream=None)
    pdom_db.preprocess_prot(logstream=None)


def test_protids():
    """Pdtl: extract protein IDs from GFF3"""
    config = genhub.test_registry.genome('Pdtl')
    db = PdomDB('Pdtl', config)

    protids = ['PdomMRNAr1.2-08518.1', 'PdomMRNAr1.2-11420.1',
               'PdomMRNAr1.2-08519.1']
    infile = 'testdata/gff3/pdom-266.gff3'
    testids = list()
    with open(infile, 'r') as instream:
        for protid in db.gff3_protids(instream):
            testids.append(protid)
    assert sorted(protids) == sorted(testids), \
        'protein ID mismatch: %r %r' % (protids, testids)


def test_protmap():
    """Pdtl: extract protein-->iLocus mapping from GFF3"""
    config = genhub.test_registry.genome('Pdtl')
    db = PdomDB('Pdtl', config)

    mapping = {'PdomMRNAr1.2-08518.1': 'PdomILC-18235',
               'PdomMRNAr1.2-11420.1': 'PdomILC-18237',
               'PdomMRNAr1.2-08519.1': 'PdomILC-18238'}
    infile = 'testdata/gff3/pdom-266-loci.gff3'
    testmap = dict()
    with open(infile, 'r') as instream:
        for protid, locid in db.protein_mapping(instream):
            testmap[protid] = locid
    assert mapping == testmap, \
        'protein mapping mismatch: %r %r' % (mapping, testmap)
