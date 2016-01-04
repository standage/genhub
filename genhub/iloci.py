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
import filecmp
import re
import subprocess
import sys
import genhub


def intervals(db, delta=500, logstream=sys.stderr):
    """
    Compute iLocus intervals.

    See the documentation for LocusPocus and the AEGeAn Toolkit for more
    details.
    """
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] computing interval loci' % db.config['species']
        print(logmsg, file=logstream)

    nameformat = db.label + 'ILC-%05lu'
    specdir = '%s/%s' % (db.workdir, db.label)
    command = 'lpdriver.py --namefmt=%s' % nameformat
    command += ' --delta=%d' % delta
    command += ' --ilenfile=%s/ilens.temp' % specdir
    command += ' --out=%s/%s.iloci.gff3' % (specdir, db.label)
    command += ' %s/%s.gff3' % (specdir, db.label)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] merging iLoci' % db.config['species']
        print(logmsg, file=logstream)
    infile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.miloci.gff3' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        subprocess.check_call('miloci.py', stdin=instream, stdout=outstream)


def simple(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] determining simple iLoci' % db.config['species']
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)
    ilocusfile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.simple-iloci.txt' % (specdir, db.label)
    with open(ilocusfile, 'r') as instream, open(outfile, 'w') as outstream:
        for line in instream:
            if '\tlocus\t' not in line:
                continue
            if 'child_mRNA=' in line and 'child_gene=1;' in line:
                namematch = re.search('Name=([^;\n]+)', line)
                ilocusname = namematch.group(1)
                print(ilocusname, file=outstream)


def representatives(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'selecting iLocus representatives'
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)
    infile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    mapfile = '%s/%s.ilocus.mrnas.txt' % (specdir, db.label)
    grepproc = subprocess.Popen(['grep', '-v', '\tintron\t', infile],
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
    pmrnaproc = subprocess.Popen(['pmrna', '--locus', '--map=%s' % mapfile],
                                 stdin=grepproc.stdout,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
    canonproc = subprocess.Popen(['canon-gff3', '--outfile=%s' % outfile],
                                 stdin=pmrnaproc.stdout,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
    stdout, stderr = canonproc.communicate()
    for line in stderr.split('\n'):
        if 'no valid mRNAs' not in line and line != '':  # pragma: no cover
            print(line, file=logstream)


def sequences(db, logstream=sys.stderr):
    """Extract iLocus sequences."""
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting iLocus sequences'
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    fastain = '%s/%s.gdna.fa' % (specdir, db.label)
    for ltype in ['iloci', 'miloci']:
        outfile = '%s/%s.%s.fa' % (specdir, db.label, ltype)
        gff3in = '%s/%s.%s.gff3' % (specdir, db.label, ltype)
        command = 'xtractore --debug --type=locus '
        command += '--outfile=%s %s %s' % (outfile, gff3in, fastain)
        cmd = command.split(' ')
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                                universal_newlines=True)
        stdout, stderr = proc.communicate()
        for line in stderr.split('\n'):
            if 'has not been previously introduced' not in line and \
               'does not begin with "##gff-version"' not in line and \
               line != '':  # pragma: no cover
                print(line, file=logstream)
        assert proc.returncode == 0, 'command failed: ' + command


def ancillary(db, logstream=sys.stderr):
    """Process iLocus ancillary data."""
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] computing interval loci' % db.config['species']
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    cmd = ['sed', 's/^/%s\t/' % db.label, '%s/ilens.temp' % specdir]
    ilensfile = '%s/%s.ilens.tsv' % (specdir, db.label)
    with open(ilensfile, 'w') as outstream:
        subprocess.check_call(cmd, stdout=outstream)

    ilocusfile = '%s/%s.iloci.gff3' % (specdir, db.label)
    cmd = ['genhub-filens.py', db.label, ilocusfile]
    filensfile = '%s/%s.filens.tsv' % (specdir, db.label)
    with open(filensfile, 'w') as outstream:
        subprocess.check_call(cmd, stdout=outstream)

    infile = '%s/%s.ilocus.mrnas.txt' % (specdir, db.label)
    outfile = '%s/%s.mrnas.txt' % (specdir, db.label)
    with open(outfile, 'w') as outstream:
        subprocess.check_call(['cut', '-f', '2', infile], stdout=outstream)


# -----------------------------------------------------------------------------
# Driver function
# -----------------------------------------------------------------------------

def prepare(db, delta=500, logstream=sys.stderr):  # pragma: no cover
    intervals(db, delta=delta, logstream=logstream)
    simple(db, logstream=logstream)
    representatives(db, logstream=logstream)
    sequences(db, logstream=logstream)
    ancillary(db, logstream=logstream)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_intervals():
    """Parse iLocus intervals"""
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    intervals(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.iloci.gff3'
    testfile = 'testdata/gff3/bdis-iloci.gff3'
    assert filecmp.cmp(outfile, testfile), 'iLocus parsing failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.ilens.tsv'
    testfile = 'testdata/misc/bdis-ilens.tsv'
    assert filecmp.cmp(outfile, testfile), 'iLocus length reporting failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.filens.tsv'
    testfile = 'testdata/misc/bdis-filens.tsv'
    assert filecmp.cmp(outfile, testfile), \
        'flanking iLocus length reporting failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.miloci.gff3'
    testfile = 'testdata/gff3/bdis-miloci.gff3'
    assert filecmp.cmp(outfile, testfile), 'miLocus parsing failed'


def test_simple():
    """Determine simple iLoci"""
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    simple(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.simple-iloci.txt'
    testfile = 'testdata/misc/bdis-simple.txt'
    assert filecmp.cmp(outfile, testfile), 'simple iLocus ID failed'


def test_reps():
    """Select representative gene models for each iLocus"""
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    representatives(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.ilocus.mrnas.gff3'
    testfile = 'testdata/gff3/bdis-reps.gff3'
    assert filecmp.cmp(outfile, testfile), 'iLocus rep ID failed'


def test_sequences():
    """Extract iLocus sequences"""
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    sequences(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.iloci.fa'
    testfile = 'testdata/fasta/bdis-iloci.fa'
    assert filecmp.cmp(outfile, testfile), 'iLocus sequence extraction failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.miloci.fa'
    testfile = 'testdata/fasta/bdis-miloci.fa'
    assert filecmp.cmp(outfile, testfile), 'miLocus sequence extraction failed'


def test_ancillary():
    """Process ancillary data for iLoci"""
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    ancillary(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.ilens.tsv'
    testfile = 'testdata/misc/bdis-ilens.tsv'
    assert filecmp.cmp(outfile, testfile), 'iLocus length record failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.filens.tsv'
    testfile = 'testdata/misc/bdis-filens.tsv'
    assert filecmp.cmp(outfile, testfile), 'flanking iLocus length failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.ilocus.mrnas.txt'
    testfile = 'testdata/misc/bdis-ilocus-mrnas.txt'
    assert filecmp.cmp(outfile, testfile), 'iLocus rep cut failed'
