#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Module for extracting various data types from a genome annotation."""

from __future__ import print_function
import filecmp
import re
import subprocess
import sys
import genhub


def ilocus_intervals(db, delta=500, logstream=sys.stderr):
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

    cmd = ['sed', 's/^/%s\t/' % db.label, '%s/ilens.temp' % specdir]
    ilensfile = '%s/%s.ilens.tsv' % (specdir, db.label)
    with open(ilensfile, 'w') as outstream:
        subprocess.check_call(cmd, stdout=outstream)

    ilocusfile = '%s/%s.iloci.gff3' % (specdir, db.label)
    cmd = ['genhub-filens.py', db.label, ilocusfile]
    filensfile = '%s/%s.filens.tsv' % (specdir, db.label)
    with open(filensfile, 'w') as outstream:
        subprocess.check_call(cmd, stdout=outstream)

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] merging iLoci' % db.config['species']
        print(logmsg, file=logstream)
    infile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.miloci.gff3' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        subprocess.check_call('miloci.py', stdin=instream, stdout=outstream)


def ilocus_sequences(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting iLocus sequences'
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    outfile = '%s/%s.iloci.fa' % (specdir, db.label)
    command = 'xtractore --nameisid --type=locus --outfile=%s' % outfile
    command += ' %s/%s.iloci.gff3' % (specdir, db.label)
    command += ' %s/%s.gdna.fa' % (specdir, db.label)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    outfile = '%s/%s.miloci.fa' % (specdir, db.label)
    command = 'xtractore --type=locus --outfile=%s' % outfile
    command += ' %s/%s.miloci.gff3' % (specdir, db.label)
    command += ' %s/%s.gdna.fa' % (specdir, db.label)
    cmd = command.split(' ')
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                            universal_newlines=True)
    stdout, stderr = proc.communicate()
    for line in stderr.split('\n'):
        if 'has not been previously introduced' not in line and \
           'does not begin with "##gff-version"' not in line and \
           line != '':  # pragma: no cover
            print(line, file=logstream)


def ilocus_representatives(db, logstream=sys.stderr):
    specdir = '%s/%s' % (db.workdir, db.label)
    ilocusfile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.simple-iloci.txt' % (specdir, db.label)
    with open(ilocusfile, 'r') as instream, open(outfile, 'w') as outstream:
        for line in instream:
            if '\tlocus\t' not in line:
                continue
            if 'mRNA=' in line and 'gene=1;' in line:
                namematch = re.search('Name=([^;\n]+)', line)
                ilocusname = namematch.group(1)
                print(ilocusname, file=outstream)

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'selecting iLocus representatives'
        print(logmsg, file=logstream)
    infile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    mapfile = '%s/%s.ilocus.mrnas.txt' % (specdir, db.label)
    grepproc = subprocess.Popen(['grep', '-v', '\tintron\t', infile],
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
    pmrnaproc = subprocess.Popen(['pmrna', '--locus', '--accession',
                                  '--map=%s' % mapfile],
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

    infile = '%s/%s.ilocus.mrnas.txt' % (specdir, db.label)
    outfile = '%s/%s.mrnas.txt' % (specdir, db.label)
    with open(outfile, 'w') as outstream:
        subprocess.check_call(['cut', '-f', '2', infile], stdout=outstream)


def protein_ids(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] selecting protein IDs' % db.config['species']
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    outfile = '%s/%s.protids.txt' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        for protid in db.gff3_protids(instream):
            print(protid, file=outstream)


def protein_sequences(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting protein sequences'
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    idfile = '%s/%s.protids.txt' % (specdir, db.label)
    seqfile = '%s/%s.all.prot.fa' % (specdir, db.label)
    outfile = '%s/%s.prot.fa' % (specdir, db.label)
    with open(idfile, 'r') as idstream, \
            open(seqfile, 'r') as seqstream, \
            open(outfile, 'w') as outstream:
        for defline, seq in genhub.fasta.select(idstream, seqstream):
            defline = '>gnl|%s|%s' % (db.label, defline[1:])
            print(defline, end='', file=outstream)
            genhub.fasta.format(seq, outstream=outstream)


def protein_mapping(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'parsing protein->iLocus mapping'
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    infile = '%s/%s.iloci.gff3' % (specdir, db.label)
    outfile = '%s/%s.protein2ilocus.txt' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        for protid, ilocusid in db.protein_mapping(instream):
            print(protid, ilocusid, sep='\t', file=outstream)


# -----------------------------------------------------------------------------
# Driver functions
# -----------------------------------------------------------------------------

def get_iloci(db, delta=500, logstream=sys.stderr):  # pragma: no cover
    ilocus_intervals(db, delta=delta, logstream=logstream)
    ilocus_sequences(db, logstream=logstream)
    ilocus_representatives(db, logstream=logstream)


def get_proteins(db, delta=500, logstream=sys.stderr):  # pragma: no cover
    protein_ids(db, logstream=logstream)
    protein_sequences(db, logstream=logstream)
    protein_mapping(db, logstream=logstream)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_ilocus_intervals():
    """Parse iLocus intervals"""
    label, config = genhub.conf.load_one('conf/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    ilocus_intervals(db, logstream=None)

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


def test_ilocus_sequence():
    """Extract iLocus sequences"""
    label, config = genhub.conf.load_one('conf/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    ilocus_sequences(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.iloci.fa'
    testfile = 'testdata/fasta/bdis-iloci.fa'
    assert filecmp.cmp(outfile, testfile), 'iLocus sequence extraction failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.miloci.fa'
    testfile = 'testdata/fasta/bdis-miloci.fa'
    assert filecmp.cmp(outfile, testfile), 'miLocus sequence extraction failed'


def test_ilocus_reps():
    """Identify iLocus representatives"""
    label, config = genhub.conf.load_one('conf/Bdis.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    ilocus_representatives(db, logstream=None)

    outfile = 'testdata/demo-workdir/Bdis/Bdis.simple-iloci.txt'
    testfile = 'testdata/misc/bdis-simple-iloci.txt'
    assert filecmp.cmp(outfile, testfile), 'simple iLocus ID failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.ilocus.mrnas.gff3'
    testfile = 'testdata/gff3/bdis-ilocus-mrnas.gff3'
    assert filecmp.cmp(outfile, testfile), 'iLocus rep annotation failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.ilocus.mrnas.txt'
    testfile = 'testdata/misc/bdis-ilocus-mrnas.txt'
    assert filecmp.cmp(outfile, testfile), 'iLocus rep (iLocus) ID failed'

    outfile = 'testdata/demo-workdir/Bdis/Bdis.mrnas.txt'
    testfile = 'testdata/misc/bdis-mrnas.txt'
    assert filecmp.cmp(outfile, testfile), 'iLocus rep (mRNA) ID failed'
