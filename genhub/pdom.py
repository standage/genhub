#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Genome database implementation for *Polites dominula* genome data."""

from __future__ import print_function
import filecmp
import gzip
import re
import subprocess
import sys
import genhub


class PdomDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(PdomDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'pdom'
        self.specbase = 'http://de.iplantcollaborative.org/dl/d'

    def __repr__(self):
        return 'PdomDataStore'

    @property
    def gdnaurl(self):
        prefix = '53B7319E-3201-4087-9607-2D541FF34DD0'
        return '%s/%s/%s' % (self.specbase, prefix, self.gdnafilename)

    @property
    def gff3url(self):
        prefix = 'E4944CBB-7DE4-4CA1-A889-3D2A5D2E8696'
        return '%s/%s/%s' % (self.specbase, prefix, self.gff3filename)

    @property
    def proturl(self):
        prefix = 'ACD29139-6619-48DF-A9F2-F75CA382E248'
        return '%s/%s/%s' % (self.specbase, prefix, self.protfilename)

    def format_gdna(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            # No processing required currently.
            # If any is ever needed, do it here.
            print(line, end='', file=outstream)

    def format_prot(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            # No processing required currently.
            # If any is ever needed, do it here.
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        command = ['genhub-format-gff3.py', '--source', 'pdom', '--outfile',
                   self.gff3file, self.gff3path]
        subprocess.check_call(command)

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


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_download():
    """PdomDataStore download"""
    config = genhub.test_registry.genome('Pdom')
    pdom_db = PdomDB('Pdom', config)

    assert pdom_db.gdnaurl == ('http://de.iplantcollaborative.org/dl/d/'
                               '53B7319E-3201-4087-9607-2D541FF34DD0/'
                               'pdom-scaffolds-unmasked-r1.2.fa.gz')
    assert pdom_db.gff3url == ('http://de.iplantcollaborative.org/dl/d/'
                               'E4944CBB-7DE4-4CA1-A889-3D2A5D2E8696/'
                               'pdom-annot-r1.2.gff3')
    assert pdom_db.proturl == ('http://de.iplantcollaborative.org/dl/d/'
                               'ACD29139-6619-48DF-A9F2-F75CA382E248/'
                               'pdom-annot-r1.2-proteins.fa')
    assert '%r' % pdom_db == 'PdomDataStore'


def test_format():
    """Pdom formatting task"""
    config = genhub.test_registry_supp.genome('Pdom')
    pdom_db = PdomDB('Pdom', config, workdir='testdata/demo-workdir')

    pdom_db.preprocess_gdna(logstream=None)
    pdom_db.preprocess_gff3(logstream=None)
    pdom_db.preprocess_prot(logstream=None)


def test_protids():
    """Pdom: extract protein IDs from GFF3"""
    config = genhub.test_registry.genome('Pdom')
    db = PdomDB('Pdom', config)

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
    """Pdom: extract protein-->iLocus mapping from GFF3"""
    config = genhub.test_registry.genome('Pdom')
    db = PdomDB('Pdom', config)

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
