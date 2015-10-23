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
import gzip
import os
import re
import subprocess
import sys
import genhub


def gdna(label, conf, workdir='.', logstream=sys.stderr, outstream=None):
    """
    Format genomic DNA files.

    To write to a custom output destination, set `outstream` to a writeable
    file handle, stringio, or similar object.
    """

    assert 'source' in conf
    assert conf['source'] in ['ncbi', 'ncbi_flybase', 'custom']

    if logstream is not None:
        logmsg = '[GenHub: %s] ' % conf['species']
        logmsg += 'simplify genome Fasta deflines'
        print(logmsg, file=logstream)

    if conf['source'] == 'ncbi':
        if 'scaffolds' in conf:
            gdnafile = conf['scaffolds']
        else:
            gdnafile = '%s.orig.fa.gz' % label
        infile = '%s/%s/%s' % (workdir, label, gdnafile)
        assert os.path.exists(infile), \
            'file "%s" not found; check "download" task' % infile
        instream = gzip.open(infile, 'rt')
        if outstream is None:
            outfile = '%s/%s/%s.gdna.fa' % (workdir, label, label)
            outstream = open(outfile, 'w')

        for line in instream:
            line = re.sub('>gi\|\d+\|(ref|gb)\|([^\|]+)\S+', '>\g<2>', line)
            print(line, end='', file=outstream)
        instream.close()


def proteins(label, conf, workdir='.', logstream=sys.stderr, outstream=None):
    """
    Format protein sequence files.

    To write to a custom output destination, set `outstream` to a writeable
    file handle, stringio, or similar object.
    """

    assert 'source' in conf
    assert conf['source'] in ['ncbi', 'ncbi_flybase', 'custom']

    if logstream is not None:
        logmsg = '[GenHub: %s] ' % conf['species']
        logmsg += 'simplify protein Fasta deflines'
        print(logmsg, file=logstream)

    if conf['source'] == 'ncbi':
        infile = '%s/%s/protein.fa.gz' % (workdir, label)
        assert os.path.exists(infile), \
            'file "%s" not found; check "download" task' % infile
        instream = gzip.open(infile, 'rt')
        if outstream is None:
            outfile = '%s/%s/%s.all.prot.fa' % (workdir, label, label)
            outstream = open(outfile, 'w')

        for line in instream:
            line = re.sub('>gi\|\d+\|(ref|gb)\|([^\|]+)\S+', '>\g<2>', line)
            print(line, end='', file=outstream)
        instream.close()
