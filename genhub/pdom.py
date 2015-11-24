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


def gdna(label, conf, workdir='.', logstream=sys.stderr):
    """Decompression only, no processing required."""
    inpath = '%s/%s/%s' % (workdir, label, conf['scaffolds'])
    outpath = '%s/%s/%s.gdna.fa' % (workdir, label, label)
    with gzip.open(inpath, 'rt') as infile, open(outpath, 'w') as outfile:
        for line in infile:
            print(line, end='', file=outfile)


def proteins(label, conf, workdir='.', logstream=sys.stderr):
    """Decompression only, no processing required."""
    inpath = '%s/%s/%s.gz' % (workdir, label, conf['proteins'])
    outpath = '%s/%s/%s.all.prot.fa' % (workdir, label, label)
    with gzip.open(inpath, 'rt') as infile, open(outpath, 'w') as outfile:
        for line in infile:
            print(line, end='', file=outfile)


def annotation(label, conf, workdir='.', logstream=sys.stderr):
    """Preprocess annotations"""
    inpath = '%s/%s/%s' % (workdir, label, conf['annotation'])
    outpath = '%s/%s/%s.gff3' % (workdir, label, label)
    command = 'genhub-format-gff3.py --outfile %s %s' % (outpath, inpath)
    subprocess.check_call(command.split(' '))


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_download():
    """PdomDataStore download"""
    label, config = genhub.conf.load_one('conf/HymHub/Pdom.yml')
    pdom_db = PdomDB(label, config)
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

    label, conf = genhub.conf.load_one('conf/Pdom-ut.yml')
    wd = 'testdata/demo-workdir'
    genhub.format.gdna(label, conf, workdir=wd, logstream=None)
    genhub.format.proteins(label, conf, workdir=wd, logstream=None)
    genhub.format.annotation(label, conf, workdir=wd, logstream=None)
