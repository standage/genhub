#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""
Genome database implementation for data from CRG.

Two aculeate insect data sets from the Centre de Regulacio Genomica.
"""

from __future__ import print_function
import subprocess
import sys
import genhub


class CrgDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(CrgDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'crg'
        self.specbase = 'http://wasp.crg.eu'

    def __repr__(self):
        return 'CRG'

    @property
    def gdnaurl(self):
        return '%s/%s' % (self.specbase, self.gdnafilename)

    @property
    def gff3url(self):
        return '%s/%s' % (self.specbase, self.config['annotation'])

    @property
    def proturl(self):
        return '%s/%s' % (self.specbase, self.protfilename)

    @property
    def gff3filename(self):
        return '%s.gz' % self.config['annotation']

    def format_gdna(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.startswith('>'):
                line = line.replace('scaffold_', '%sScf_' % self.label)
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
        cmds.append("sed 's/	transcript	/	mRNA	/'")
        cmds.append("sed 's/scaffold_/%sScf_/'" % self.label)
        cmds.append("sed 's/scaffold/%sScf_/'" % self.label)
        cmds.append('genhub-format-gff3.py --source crg -')
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
               line != '':
                print(line, file=logstream)
        assert proc.returncode == 0, \
            'annot cleanup command failed: %s' % commands


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds():
    """CRG scaffolds download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    testurl = 'http://wasp.crg.eu/DQUA.v01.fa.gz'
    testpath = './Dqua/DQUA.v01.fa.gz'
    dqua_db = CrgDB(label, config)
    assert dqua_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (dqua_db.gdnaurl, testurl)
    assert dqua_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (dqua_db.gdnapath, testpath)
    assert '%r' % dqua_db == 'CRG'


def test_annot():
    """CRG annotation download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    testurl = 'http://wasp.crg.eu/DQUA.v01.gff3'
    testpath = 'CRG/Dqua/DQUA.v01.gff3.gz'
    testresult = (testurl, testpath)
    dqua_db = CrgDB(label, config, workdir='CRG')
    assert dqua_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (dqua_db.gff3url, testurl)
    assert dqua_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (dqua_db.gff3path, testpath)


def test_proteins():
    """CRG protein download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    testurl = 'http://wasp.crg.eu/DQUA.v01.pep.fa.gz'
    testpath = '/opt/db/genhub/Dqua/DQUA.v01.pep.fa.gz'
    dqua_db = CrgDB(label, config, workdir='/opt/db/genhub')
    assert dqua_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (dqua_db.proturl, testurl)
    assert dqua_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (dqua_db.protpath, testpath)


def test_format():
    """GenomeDB task drivers"""
    label, conf = genhub.conf.load_one('conf/Pcan-ut.yml')
    pcan_db = CrgDB(label, conf, workdir='testdata/demo-workdir')
    pcan_db.format(logstream=None)
