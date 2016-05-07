#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

from __future__ import print_function
import filecmp
import sys
import genhub


def ids(db, logstream=sys.stderr):  # pragma: no cover
    """
    Retrieve protein IDs/accessions from the genome annotation.

    The `db` variable, a `GenomeDB` object, must implement a `gff3_protids`
    method for this retrieval.
    """
    if logstream is not None:
        logmsg = '[GenHub: %s] retrieving protein IDs' % db.config['species']
        print(logmsg, file=logstream)

    specdir = '%s/%s' % (db.workdir, db.label)
    infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    outfile = '%s/%s.protids.txt' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        for protid in db.gff3_protids(instream):
            print(protid, file=outstream)


def sequences(db, logstream=sys.stderr):
    """Extract protein sequences."""
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
            print(defline, file=outstream)
            genhub.fasta.format(seq, outstream=outstream)


def mapping(db, logstream=sys.stderr):  # pragma: no cover
    """
    Retrieve mapping of protein IDs to iLocus IDs.

    The `db` variable, a `GenomeDB` object, must implement a `protein_mapping`
    method for this retrieval.
    """
    if logstream is not None:
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
# Driver function
# -----------------------------------------------------------------------------

def prepare(db, logstream=sys.stderr):  # pragma: no cover
    ids(db, logstream=logstream)
    sequences(db, logstream=logstream)
    mapping(db, logstream=logstream)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_protein_sequence():
    """Breakdown: select protein sequences"""
    db = genhub.test_registry.genome('Scer', workdir='testdata/demo-workdir')
    sequences(db, logstream=None)
    outfile = 'testdata/demo-workdir/Scer/Scer.prot.fa'
    testfile = 'testdata/fasta/scer-few-prots.fa'
    assert filecmp.cmp(outfile, testfile), 'Protein sequence selection failed'
