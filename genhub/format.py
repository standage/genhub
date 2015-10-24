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
import gzip
import os
import re
import subprocess
import sys
import genhub


def gdna(label, conf, workdir='.', instream=None, outstream=None,
         logstream=sys.stderr):
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

    if conf['source'] == 'ncbi':
        closeinstream = False
        if instream is None:
            closeinstream = True
            if 'scaffolds' in conf:
                gdnafile = conf['scaffolds']
            else:
                gdnafile = '%s.orig.fa.gz' % label
            infile = '%s/%s/%s' % (workdir, label, gdnafile)
            assert os.path.exists(infile), \
                'file "%s" not found; check "download" task' % infile
            instream = gzip.open(infile, 'rt')

        closeoutstream = False
        if outstream is None:
            closeoutstream = True
            outfile = '%s/%s/%s.gdna.fa' % (workdir, label, label)
            outstream = open(outfile, 'w')

        for line in instream:
            line = re.sub('>gi\|\d+\|(ref|gb)\|([^\|]+)\S+', '>\g<2>', line)
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()


def proteins(label, conf, workdir='.', instream=None, outstream=None,
             logstream=sys.stderr):
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

    if conf['source'] == 'ncbi':
        closeinstream = False
        if instream is None:
            closeinstream = True
            infile = '%s/%s/protein.fa.gz' % (workdir, label)
            assert os.path.exists(infile), \
                'file "%s" not found; check "download" task' % infile
            instream = gzip.open(infile, 'rt')

        closeoustream = False
        if outstream is None:
            closeoutstream = True
            outfile = '%s/%s/%s.all.prot.fa' % (workdir, label, label)
            outstream = open(outfile, 'w')

        for line in instream:
            line = re.sub('>gi\|\d+\|(ref|gb)\|([^\|]+)\S+', '>\g<2>', line)
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_gdna_ncbi():
    """NCBI gDNA formatting"""

    import filecmp

    testoutfile = 'testdata/fasta/hsal-first-7-out.fa'
    label, conf = genhub.conf.load_one('conf/HymHub/Hsal.yml')

    infile = 'testdata/fasta/hsal-first-7.fa.gz'
    instream = gzip.open(infile, 'rt')
    outfile = 'testdata/scratch/hsal-first-7.fa'
    outstream = open(outfile, 'w')
    gdna(label, conf, instream=instream, outstream=outstream, logstream=None)
    instream.close()
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal gDNA formatting failed (instream --> outstream)'

    wd = 'testdata/demo-workdir'
    outstream = open(outfile, 'w')
    gdna(label, conf, workdir=wd, outstream=outstream, logstream=None)
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
    gdna(label, conf, workdir=wd, outstream=outstream, logstream=None)
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Tcas gDNA formatting failed (dir --> outstream)'
