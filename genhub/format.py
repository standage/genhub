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
Module for pre-processing, streamlining, and standardizing data files.

Data from various sources come with different defline formats and GFF3 encoding
conventions, and comparing data across these different sources often requires
standardizing. Code in this module gives all of the sequence and annotation
files a consistent format for feature extraction and comparison.
"""

from __future__ import print_function
from io import StringIO
import filecmp
import gzip
import re
import subprocess
import sys
import genhub


infile_message = 'please verify that "download" task completed successfully'


def gdna(label, conf, workdir='.', instream=None, outstream=None,
         logstream=sys.stderr, verify=True):
    """
    Format genomic DNA files.

    To read from or write to a custom input/output streams (rather than the
    default file locations), set `instream` and/or `outstream` to a readable or
    writeable file handle, a stringio, or similar object.
    """

    assert 'source' in conf
    assert conf['source'] in ['ncbi', 'ncbi_flybase', 'custom']

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % conf['species']
        logmsg += 'simplify genome Fasta deflines'
        print(logmsg, file=logstream)

    outbase = '%s.gdna.fa' % label
    outfile = genhub.file_path(outbase, label, workdir=workdir)

    if conf['source'] == 'ncbi':
        closeinstream = False
        if instream is None:
            closeinstream = True
            if 'scaffolds' in conf:
                gdnafile = conf['scaffolds']
            else:
                gdnafile = '%s.orig.fa.gz' % label
            infile = genhub.file_path(gdnafile, label, workdir, check=True,
                                      message=infile_message)
            instream = gzip.open(infile, 'rt')

        closeoutstream = False
        if outstream is None:
            closeoutstream = True
            outstream = open(outfile, 'w')

        for line in instream:
            line = re.sub('>gi\|\d+\|(ref|gb)\|([^\|]+)\S+', '>\g<2>', line)
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()

    if verify is False:
        return

    if 'checksums' in conf and 'gdna' in conf['checksums']:
        testsha1 = genhub.file_sha1(outfile)
        assert testsha1 == conf['checksums']['gdna'], \
            '%s gDNA file integrity check failed' % label
    else:  # pragma: no cover
        message = 'Cannot verify integrity of %s gDNA file ' % label
        message += 'without a checksum'
        print(message, file=logstream)


def proteins(label, conf, workdir='.', instream=None, outstream=None,
             logstream=sys.stderr, verify=True):
    """
    Format protein sequence files.

    To read from or write to a custom input/output streams (rather than the
    default file locations), set `instream` and/or `outstream` to a readable or
    writeable file handle, a stringio, or similar object.
    """

    assert 'source' in conf
    assert conf['source'] in ['ncbi', 'ncbi_flybase', 'custom']

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % conf['species']
        logmsg += 'simplify protein Fasta deflines'
        print(logmsg, file=logstream)

    outbase = '%s.all.prot.fa' % label
    outfile = genhub.file_path(outbase, label, workdir)

    if conf['source'] == 'ncbi':
        closeinstream = False
        if instream is None:
            closeinstream = True
            infile = genhub.file_path('protein.fa.gz', label, workdir,
                                      check=True, message=infile_message)
            instream = gzip.open(infile, 'rt')

        closeoutstream = False
        if outstream is None:
            closeoutstream = True
            outstream = open(outfile, 'w')

        for line in instream:
            line = re.sub('>gi\|\d+\|(ref|gb)\|([^\|]+)\S+', '>\g<2>', line)
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()

    if verify is False:
        return

    if 'checksums' in conf and 'prot' in conf['checksums']:
        testsha1 = genhub.file_sha1(outfile)
        assert testsha1 == conf['checksums']['prot'], \
            '%s protein file integrity check failed' % label
    else:  # pragma: no cover
        message = 'Cannot verify integrity of %s protein file ' % label
        message += 'without a checksum'
        print(message, file=logstream)


def annotation(label, conf, workdir='.', logstream=sys.stderr, verify=True):
    """Clean up and standardize genome annotation."""

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] clean up annotation' % conf['species']
        print(logmsg, file=logstream)

    infile = genhub.file_path(conf['annotation'], label, workdir, check=True,
                              message=infile_message)
    outfile = genhub.file_path('%s.gff3' % label, label, workdir)
    filterstr = 'nofilter'
    if 'annotfilter' in conf:
        filterstr = conf['annotfilter']
    cmd = 'genhub-filter.sh %s %s %s' % (infile, outfile, filterstr)
    cmdargs = cmd.split(' ')
    process = subprocess.Popen(cmdargs, stderr=subprocess.PIPE,
                               universal_newlines=True)
    process.wait()
    for line in process.stderr:  # pragma: no cover
        if 'has not been previously introduced' not in line and \
           'does not begin with "##gff-version"' not in line:
            print(line, end='', file=logstream)
    assert process.returncode == 0, 'annot cleanup command failed: %s' % cmd

    if verify is False:
        return

    if 'checksums' in conf and 'gff3' in conf['checksums']:
        testsha1 = genhub.file_sha1(outfile)
        assert testsha1 == conf['checksums']['gff3'], \
            '%s annotation file integrity check failed' % label
    else:  # pragma: no cover
        message = 'Cannot verify integrity of %s annotation file ' % label
        message += 'without a checksum'
        print(message, file=logstream)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_gdna_ncbi():
    """NCBI gDNA formatting"""

    testoutfile = 'testdata/fasta/hsal-first-7-out.fa'
    label, conf = genhub.conf.load_one('conf/test2/Hsal.yml')

    infile = 'testdata/fasta/hsal-first-7.fa.gz'
    instream = gzip.open(infile, 'rt')
    outfile = 'testdata/scratch/hsal-first-7.fa'
    outstream = open(outfile, 'w')
    gdna(label, conf, instream=instream, outstream=outstream, logstream=None,
         verify=False)
    instream.close()
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal gDNA formatting failed (instream --> outstream)'

    wd = 'testdata/demo-workdir'
    outstream = open(outfile, 'w')
    gdna(label, conf, workdir=wd, outstream=outstream, logstream=None,
         verify=False)
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal gDNA formatting failed (dir --> outstream)'

    wd = 'testdata/scratch'
    subprocess.call(['mkdir', '-p', 'testdata/scratch/Hsal'])
    instream = gzip.open(infile, 'rt')
    gdna(label, conf, workdir=wd, instream=instream, logstream=None)
    instream.close()
    outfile = 'testdata/scratch/Hsal/Hsal.gdna.fa'
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal gDNA formatting failed (instream --> dir)'

    testoutfile = 'testdata/fasta/tcas-first-33-out.fa'
    label, conf = genhub.conf.load_one('conf/HymHub/Tcas.yml')

    wd = 'testdata/demo-workdir'
    outfile = 'testdata/scratch/tcas-first-33.fa'
    outstream = open(outfile, 'w')
    gdna(label, conf, workdir=wd, outstream=outstream, logstream=None,
         verify=False)
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Tcas gDNA formatting failed (dir --> outstream)'


def test_proteins_ncbi():
    """NCBI protein formatting"""

    label, conf = genhub.conf.load_one('conf/test2/Hsal.yml')
    testoutfile = 'testdata/fasta/hsal-13-prot-out.fa'

    infile = 'testdata/fasta/hsal-13-prot.fa.gz'
    instream = gzip.open(infile, 'rt')
    outfile = 'testdata/scratch/hsal-13-prot.fa'
    outstream = open(outfile, 'w')
    proteins(label, conf, instream=instream, outstream=outstream,
             logstream=None, verify=False)
    instream.close()
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal protein formatting failed (instream --> outstream)'

    wd = 'testdata/demo-workdir'
    outstream = open(outfile, 'w')
    proteins(label, conf, workdir=wd, outstream=outstream, logstream=None,
             verify=False)
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal gDNA formatting failed (dir --> outstream)'

    wd = 'testdata/scratch'
    subprocess.call(['mkdir', '-p', 'testdata/scratch/Hsal'])
    instream = gzip.open(infile, 'rt')
    proteins(label, conf, workdir=wd, instream=instream, logstream=None)
    instream.close()
    outfile = 'testdata/scratch/Hsal/Hsal.all.prot.fa'
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal gDNA formatting failed (instream --> dir)'


def test_annotation():
    """NCBI annotation formatting"""

    label, conf = genhub.conf.load_one('conf/test2/Aech.yml')
    annotation(label, conf, workdir='testdata/demo-workdir', logstream=None)
    outfile = 'testdata/demo-workdir/Aech/Aech.gff3'
    testfile = 'testdata/gff3/ncbi-format-aech.gff3'
    assert filecmp.cmp(outfile, testfile), 'Aech annotation formatting failed'

    label, conf = genhub.conf.load_one('conf/test2/Pbar.yml')
    annotation(label, conf, workdir='testdata/demo-workdir', logstream=None,
               verify=False)
    outfile = 'testdata/demo-workdir/Pbar/Pbar.gff3'
    testfile = 'testdata/gff3/ncbi-format-pbar.gff3'
    assert filecmp.cmp(outfile, testfile), 'Pbar annotation formatting failed'
