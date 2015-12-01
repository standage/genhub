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
import filecmp
import gzip
import subprocess
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

    def format_gdna(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.startswith('>'):
                line = line.replace('scaffold', '%sScf_' % self.label)
            print(line, end='', file=outstream)

    def format_prot(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            # No processing required currently.
            # If any is ever needed, do it here.
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('gunzip -c %s' % self.gff3path)
        cmds.append('genhub-namedup.py')
        cmds.append("sed 's/scaffold/%sScf_/'" % self.label)
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
               'illegal uppercase attribute "Shift"' not in line and \
               'has the wrong phase' not in line and \
               line != '':
                print(line, file=logstream)
        assert proc.returncode == 0, \
            'annot cleanup command failed: %s' % commands


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds_download():
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


def test_annot_download():
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


def test_proteins_download():
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


def test_gdna_format():
    """BeeBase gDNA formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hlab.yml')
    hlab_db = BeeBaseDB(label, conf, workdir='testdata/demo-workdir')
    hlab_db.preprocess_gdna(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hlab/Hlab.gdna.fa'
    testoutfile = 'testdata/fasta/hlab-first-6-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Hlab gDNA formatting failed'


def test_annotation_beebase():
    """BeeBase annotation formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hlab.yml')
    hlab_db = BeeBaseDB(label, conf, workdir='testdata/demo-workdir')
    hlab_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hlab/Hlab.gff3'
    testfile = 'testdata/gff3/beebase-format-hlab.gff3'
    assert filecmp.cmp(outfile, testfile), 'Hlab annotation formatting failed'


def test_proteins_beebase():
    """BeeBase protein formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hlab.yml')
    hlab_db = BeeBaseDB(label, conf, workdir='testdata/demo-workdir')
    hlab_db.preprocess_prot(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hlab/Hlab.all.prot.fa'
    testoutfile = 'testdata/fasta/hlab-first-20-prot-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Hlab protein formatting failed'
