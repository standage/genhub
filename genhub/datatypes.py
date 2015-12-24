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
    command = 'xtractore --debug --type=locus --outfile=%s' % outfile
    command += ' %s/%s.iloci.gff3' % (specdir, db.label)
    command += ' %s/%s.gdna.fa' % (specdir, db.label)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    outfile = '%s/%s.miloci.fa' % (specdir, db.label)
    command = 'xtractore --debug --type=locus --outfile=%s' % outfile
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

    infile = '%s/%s.ilocus.mrnas.txt' % (specdir, db.label)
    outfile = '%s/%s.mrnas.txt' % (specdir, db.label)
    with open(outfile, 'w') as outstream:
        subprocess.check_call(['cut', '-f', '2', infile], stdout=outstream)


def protein_ids(db, logstream=sys.stderr):  # pragma: no cover
    if logstream is not None:
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
            print(defline, file=outstream)
            genhub.fasta.format(seq, outstream=outstream)


def protein_mapping(db, logstream=sys.stderr):  # pragma: no cover
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


def mrna_exons(instream, convert=False, keepMrnas=False, usecds=False):
    mrnaids = {}
    for line in instream:
        line = line.rstrip()
        fields = line.split('\t')
        if len(fields) != 9:
            continue
        exontype = 'exon'
        if usecds:
            exontype = 'CDS'

        if fields[2] == 'mRNA':
            mrnaid = re.search('ID=([^;\n]+)', fields[8]).group(1)
            accmatch = re.search('accession=([^;\n]+)', fields[8])
            assert accmatch, 'Unable to parse mRNA accession: %s' % fields[8]
            mrnaacc = accmatch.group(1)
            mrnaids[mrnaid] = 1
            if not convert and keepMrnas:  # pragma: no cover
                fields[8] = re.sub('Parent=[^;\n]+;*', '', fields[8])
                yield '\t'.join(fields)

        elif fields[2] == exontype:
            parentid = re.search('Parent=([^;\n]+)', fields[8]).group(1)
            fields[7] = '.'
            if parentid in mrnaids:
                if convert:
                    fields[2] = 'mRNA'
                    fields[8] = re.sub('ID=[^;\n]+;*', '', fields[8])
                    fields[8] = fields[8].replace('Parent=', 'ID=')
                    if 'accession=' not in fields[8]:
                        fields[8] += ';accession=' + mrnaacc
                else:
                    if not keepMrnas:  # pragma: no cover
                        fields[8] = re.sub('Parent=[^;\n]+;*', '', fields[8])
                yield '\t'.join(fields)


def mature_mrna_intervals(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'calculating mature mRNA intervals'
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)

    infile = '%s/%s.gff3' % (specdir, db.label)
    outfile = '%s/%s.mrnas.temp' % (specdir, db.label)
    usecds = False
    if repr(db) == 'BeeBase':
        usecds = True
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        for exon in mrna_exons(instream, convert=True, usecds=usecds):
            print(exon, file=outstream)

    infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    outfile = '%s/%s.ilocus.mrnas.temp' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        for exon in mrna_exons(instream, convert=True):
            print(exon, file=outstream)

    inpatterns = ['%s/%s.mrnas.temp', '%s/%s.ilocus.mrnas.temp']
    outpatterns = ['%s/%s.mrnas.gff3', '%s/%s.all.mrnas.gff3']
    for inpattern, outpattern in zip(inpatterns, outpatterns):
        infile = inpattern % (specdir, db.label)
        outfile = outpattern % (specdir, db.label)
        command = 'gt gff3 -sort -tidy -force -o %s %s' % (outfile, infile)
        cmd = command.split(' ')
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                                universal_newlines=True)
        _, stderr = proc.communicate()
        for line in stderr.split('\n'):  # pragma: no cover
            if 'has not been previously introduced' not in line and \
               'does not begin with "##gff-version"' not in line and \
               line != '':
                print(line, file=logstream)


def mrna_sequences(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting pre-mRNA and mature mRNA sequences'
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)

    # All pre-mRNA sequences
    gff3infile = '%s/%s.gff3' % (specdir, db.label)
    fastainfile = '%s/%s.gdna.fa' % (specdir, db.label)
    outfile = '%s/%s.all.pre-mrnas.fa' % (specdir, db.label)
    command = 'xtractore --debug --type=mRNA --outfile=%s ' % outfile
    command += '%s %s' % (gff3infile, fastainfile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    # All mature mRNA sequences
    gff3infile = '%s/%s.all.mrnas.gff3' % (specdir, db.label)
    fastainfile = '%s/%s.gdna.fa' % (specdir, db.label)
    outfile = '%s/%s.all.mrnas.fa' % (specdir, db.label)
    command = 'xtractore --debug --type=mRNA --outfile=%s ' % outfile
    command += '%s %s' % (gff3infile, fastainfile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    # Representative pre-mRNA sequences
    idfile = '%s/%s.mrnas.txt' % (specdir, db.label)
    seqfile = '%s/%s.all.pre-mrnas.fa' % (specdir, db.label)
    outfile = '%s/%s.pre-mrnas.fa' % (specdir, db.label)
    with open(idfile, 'r') as idstream, \
            open(seqfile, 'r') as seqstream, \
            open(outfile, 'w') as outstream:
        for defline, seq in genhub.fasta.select(idstream, seqstream):
            print(defline, file=outstream)
            genhub.fasta.format(seq, outstream=outstream)

    # Representative mature mRNA sequences
    idfile = '%s/%s.mrnas.txt' % (specdir, db.label)
    seqfile = '%s/%s.all.mrnas.fa' % (specdir, db.label)
    outfile = '%s/%s.mrnas.fa' % (specdir, db.label)
    with open(idfile, 'r') as idstream, \
            open(seqfile, 'r') as seqstream, \
            open(outfile, 'w') as outstream:
        for defline, seq in genhub.fasta.select(idstream, seqstream):
            print(defline, file=outstream)
            genhub.fasta.format(seq, outstream=outstream)


def cds_sequences(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting coding sequences'
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)

    gff3infile = '%s/%s.gff3' % (specdir, db.label)
    fastainfile = '%s/%s.gdna.fa' % (specdir, db.label)
    outfile = '%s/%s.all.cds.fa' % (specdir, db.label)
    command = 'xtractore --type=CDS --outfile=%s ' % outfile
    command += '%s %s' % (gff3infile, fastainfile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    gff3infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    fastainfile = '%s/%s.gdna.fa' % (specdir, db.label)
    outfile = '%s/%s.cds.fa' % (specdir, db.label)
    command = 'xtractore --type=CDS --outfile=%s ' % outfile
    command += '%s %s' % (gff3infile, fastainfile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)


def exon_sequences(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting exon sequences'
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)

    gff3infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    fastainfile = '%s/%s.gdna.fa' % (specdir, db.label)
    outfile = '%s/%s.exons.fa' % (specdir, db.label)
    command = 'xtractore --type=exon --outfile=%s ' % outfile
    command += '%s %s' % (gff3infile, fastainfile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)


def parse_intron_accessions(instream):
    moltypes = ['mRNA', 'tRNA', 'ncRNA', 'transcript', 'primary_transcript',
                'V_gene_segment', 'D_gene_segment', 'J_gene_segment',
                'C_gene_segment']
    id_to_accession = dict()
    for line in instream:
        line = line.rstrip()
        idmatch = re.search('ID=([^;\n]+)', line)
        accmatch = re.search('accession=([^;\n]+)', line)
        if idmatch and accmatch:
            molid = idmatch.group(1)
            accession = accmatch.group(1)
            id_to_accession[molid] = accession

        if '\tintron\t' in line:
            parentid = re.search('Parent=([^;\n]+)', line).group(1)
            assert ',' not in parentid, parentid
            accession = id_to_accession[parentid]
            line += ';accession=%s' % accession

        yield(line)


def intron_sequences(db, logstream=sys.stderr):
    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % db.config['species']
        logmsg += 'extracting intron sequences'
        print(logmsg, file=logstream)
    specdir = '%s/%s' % (db.workdir, db.label)

    infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    outfile = '%s/%s.with-introns.gff3' % (specdir, db.label)
    command = 'canon-gff3 --outfile=%s %s' % (outfile, infile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)

    infile = '%s/%s.ilocus.mrnas.gff3' % (specdir, db.label)
    outfile = '%s/%s.with-introns.gff3' % (specdir, db.label)
    with open(infile, 'r') as instream, open(outfile, 'w') as outstream:
        for line in parse_intron_accessions(instream):
            print(line, file=outstream)

    gff3infile = '%s/%s.with-introns.gff3' % (specdir, db.label)
    fastainfile = '%s/%s.gdna.fa' % (specdir, db.label)
    outfile = '%s/%s.introns.fa' % (specdir, db.label)
    command = 'xtractore --type=intron --outfile=%s ' % outfile
    command += '%s %s' % (gff3infile, fastainfile)
    cmd = command.split(' ')
    subprocess.check_call(cmd)


# -----------------------------------------------------------------------------
# Driver functions
# -----------------------------------------------------------------------------

def get_iloci(db, delta=500, logstream=sys.stderr):  # pragma: no cover
    ilocus_intervals(db, delta=delta, logstream=logstream)
    ilocus_sequences(db, logstream=logstream)
    ilocus_representatives(db, logstream=logstream)


def get_proteins(db, logstream=sys.stderr):  # pragma: no cover
    protein_ids(db, logstream=logstream)
    protein_sequences(db, logstream=logstream)
    protein_mapping(db, logstream=logstream)


def get_mrnas(db, logstream=sys.stderr):  # pragma: no cover
    mature_mrna_intervals(db, logstream=logstream)
    mrna_sequences(db, logstream=logstream)


def get_exons(db, logstream=sys.stderr):  # pragma: no cover
    exon_sequences(db, logstream=logstream)
    intron_sequences(db, logstream=logstream)
    cds_sequences(db, logstream=logstream)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_ilocus_intervals():
    """Parse iLocus intervals"""
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
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
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
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
    label, config = genhub.conf.load_one('conf/modorg/Bdis.yml')
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


def test_protein_sequence():
    """Select protein sequences"""
    label, config = genhub.conf.load_one('conf/modorg/Scer.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    protein_sequences(db, logstream=None)

    outfile = 'testdata/demo-workdir/Scer/Scer.prot.fa'
    testfile = 'testdata/fasta/scer-few-prots.fa'
    assert filecmp.cmp(outfile, testfile), 'Protein sequence selection failed'


def test_mature_mrna_intervals():
    """Define mature mRNA intervals"""
    label, config = genhub.conf.load_one('conf/modorg/Atha.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    mature_mrna_intervals(db, logstream=None)

    outfile = 'testdata/demo-workdir/Atha/Atha.all.mrnas.gff3'
    testfile = 'testdata/gff3/atha-all-mrnas.gff3'
    assert filecmp.cmp(outfile, testfile), 'mature mRNA interval ID failed'

    outfile = 'testdata/demo-workdir/Atha/Atha.mrnas.gff3'
    testfile = 'testdata/gff3/atha-mrnas.gff3'
    assert filecmp.cmp(outfile, testfile), 'mature mRNA interval ID failed'

    label, config = genhub.conf.load_one('conf/hym/Dnov.yml')
    db = genhub.beebase.BeeBaseDB(label, config,
                                  workdir='testdata/demo-workdir')
    mature_mrna_intervals(db, logstream=None)

    outfile = 'testdata/demo-workdir/Dnov/Dnov.all.mrnas.gff3'
    testfile = 'testdata/gff3/dnov-all-mrnas.gff3'
    assert filecmp.cmp(outfile, testfile), 'mature mRNA interval ID failed'

    outfile = 'testdata/demo-workdir/Dnov/Dnov.mrnas.gff3'
    testfile = 'testdata/gff3/dnov-mrnas.gff3'
    assert filecmp.cmp(outfile, testfile), 'mature mRNA interval ID failed'


def test_mrna_sequences():
    """Extract mRNA sequences"""
    label, config = genhub.conf.load_one('conf/modorg/Atha.yml')
    db = genhub.refseq.RefSeqDB(label, config, workdir='testdata/demo-workdir')
    mrna_sequences(db, logstream=None)

    outfile = 'testdata/demo-workdir/Atha/Atha.all.pre-mrnas.fa'
    testfile = 'testdata/fasta/atha-all-pre-mrnas.fa'
    assert filecmp.cmp(outfile, testfile), 'all pre-mRNA seq extraction failed'

    outfile = 'testdata/demo-workdir/Atha/Atha.pre-mrnas.fa'
    testfile = 'testdata/fasta/atha-pre-mrnas.fa'
    assert filecmp.cmp(outfile, testfile), 'pre-mRNA seq extraction failed'

    outfile = 'testdata/demo-workdir/Atha/Atha.all.pre-mrnas.fa'
    testfile = 'testdata/fasta/atha-all-pre-mrnas.fa'
    assert filecmp.cmp(outfile, testfile), 'all mRNA seq extraction failed'

    outfile = 'testdata/demo-workdir/Atha/Atha.mrnas.fa'
    testfile = 'testdata/fasta/atha-mrnas.fa'
    assert filecmp.cmp(outfile, testfile), 'mature mRNA seq extraction failed'
