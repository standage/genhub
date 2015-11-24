#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Genome database implementation for BeeBase consortium data."""

from __future__ import print_function
import sys
import genhub


class BeeBaseDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(BeeBaseDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'beebase'
        self.specbase = ('http://hymenopteragenome.org/beebase/sites/'
                         'hymenopteragenome.org.beebase/files/data/'
                         'consortium_data')

    def __repr__(self):
        return 'BeeBase'

    @property
    def gdnaurl(self):
        return '%s/%s' % (self.specbase, self.gdnafilename)

    @property
    def gff3url(self):
        return '%s/%s' % (self.specbase, self.gff3filename)

    @property
    def proturl(self):
        return '%s/%s' % (self.specbase, self.protfilename)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds():
    """BeeBase consortium scaffolds download"""

    label, config = genhub.conf.load_one('conf/HymHub/Emex.yml')
    testurl = ('http://hymenopteragenome.org/beebase/sites/'
               'hymenopteragenome.org.beebase/files/data/consortium_data/'
               'Eufriesea_mexicana.v1.0.fa.gz')
    testpath = './Emex/Eufriesea_mexicana.v1.0.fa.gz'
    emex_db = BeeBaseDB(label, config)
    assert emex_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (emex_db.gdnaurl, testurl)
    assert emex_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (emex_db.gdnapath, testpath)
    assert '%r' % emex_db == 'BeeBase'


def test_annot():
    """BeeBase consortium annotation download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dnov.yml')
    testurl = ('http://hymenopteragenome.org/beebase/sites/'
               'hymenopteragenome.org.beebase/files/data/consortium_data/'
               'Dufourea_novaeangliae_v1.1.gff.gz')
    testpath = 'BeeBase/Dnov/Dufourea_novaeangliae_v1.1.gff.gz'
    dnov_db = BeeBaseDB(label, config, workdir='BeeBase')
    assert dnov_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (dnov_db.gff3url, testurl)
    assert dnov_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (dnov_db.gff3path, testpath)


def test_proteins():
    """BeeBase consortium protein download"""

    label, config = genhub.conf.load_one('conf/HymHub/Hlab.yml')
    testurl = ('http://hymenopteragenome.org/beebase/sites/'
               'hymenopteragenome.org.beebase/files/data/consortium_data/'
               'Habropoda_laboriosa_v1.2.pep.fa.gz')
    testpath = '/opt/db/genhub/Hlab/Habropoda_laboriosa_v1.2.pep.fa.gz'
    hlab_db = BeeBaseDB(label, config, workdir='/opt/db/genhub')
    assert hlab_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (hlab_db.proturl, testurl)
    assert hlab_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (hlab_db.protpath, testpath)
