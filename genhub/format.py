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
import importlib
import os
import re
import subprocess
import sys
import genhub


infile_message = 'please verify that "download" task completed successfully'
sources = ['ncbi', 'ncbi_flybase', 'beebase']


def gdna(label, conf, workdir='.', instream=None, outstream=None,
         logstream=sys.stderr, verify=True):
    """
    Format genomic DNA files.

    To read from or write to a custom input/output streams (rather than the
    default file locations), set `instream` and/or `outstream` to a readable or
    writeable file handle, a stringio, or similar object.
    """

    assert 'source' in conf
    assert conf['source'] in sources + ['custom']

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % conf['species']
        logmsg += 'preprocess genome Fasta file (clean up deflines)'
        print(logmsg, file=logstream)

    outbase = '%s.gdna.fa' % label
    outfile = genhub.file_path(outbase, label, workdir=workdir)

    if conf['source'] in ['ncbi', 'ncbi_flybase']:
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
            if line.startswith('>'):
                pattern = '>gi\|\d+\|(ref|gb)\|([^\|]+)\S+'
                line = re.sub(pattern, '>\g<2>', line)
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()

    elif conf['source'] == 'beebase':
        closeinstream = False
        if instream is None:
            closeinstream = True
            infile = genhub.file_path(conf['scaffolds'], label, workdir,
                                      check=True, message=infile_message)
            instream = gzip.open(infile, 'rt')

        closeoutstream = False
        if outstream is None:
            closeoutstream = True
            outstream = open(outfile, 'w')

        for line in instream:
            if line.startswith('>'):
                line = '>%s_%s' % (label, line[1:])
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()

    elif conf['source'] == 'custom':
        mod = importlib.import_module('genhub.' + conf['module'])
        mod.gdna(label, conf, workdir=workdir, logstream=logstream)

    if verify is False:  # pragma: no cover
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
    assert conf['source'] in sources + ['custom']

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % conf['species']
        logmsg += 'preprocess protein Fasta file (clean up deflines)'
        print(logmsg, file=logstream)

    outbase = '%s.all.prot.fa' % label
    outfile = genhub.file_path(outbase, label, workdir)

    if conf['source'] in ['ncbi', 'ncbi_flybase']:
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
            if line.startswith('>'):
                pattern = '>gi\|\d+\|(ref|gb)\|([^\|]+)\S+'
                line = re.sub(pattern, '>\g<2>', line)
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()

    if conf['source'] == 'beebase':
        closeinstream = False
        if instream is None:
            closeinstream = True
            infile = genhub.file_path(conf['proteins'], label, workdir,
                                      check=True, message=infile_message)
            instream = gzip.open(infile, 'rt')

        closeoutstream = False
        if outstream is None:
            closeoutstream = True
            outstream = open(outfile, 'w')

        for line in instream:
            # No processing required currently.
            # If any is ever needed, do it here.
            print(line, end='', file=outstream)

        if closeinstream:
            instream.close()
        if closeoutstream:
            outstream.close()

    elif conf['source'] == 'custom':
        mod = importlib.import_module('genhub.' + conf['module'])
        mod.proteins(label, conf, workdir=workdir, logstream=logstream)

    if verify is False:  # pragma: no cover
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

    assert 'source' in conf
    assert conf['source'] in sources + ['custom']

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] clean up annotation' % conf['species']
        print(logmsg, file=logstream)

    outfile = genhub.file_path('%s.gff3' % label, label, workdir)

    if conf['source'] in ['ncbi', 'ncbi_flybase', 'beebase']:
        infile = genhub.file_path(conf['annotation'], label, workdir,
                                  check=True, message=infile_message)

        cmd = 'genhub-filter.py'
        if 'annotfilter' in conf:
            excludefile = genhub.conf.conf_filter_file(conf)
            cmd += ' --exclude %s' % excludefile.name
        if conf['source'] == 'ncbi_flybase':  # pragma: no cover
            cmd += ' --fixtrna'
        if conf['source'] == 'beebase':
            cmd += ' --namedup --prefix %s_' % label
        cmd += ' %s %s' % (infile, outfile)
        cmdargs = cmd.split(' ')
        proc = subprocess.Popen(cmdargs, stderr=subprocess.PIPE,
                                universal_newlines=True)
        stdout, stderr = proc.communicate()
        for line in stderr.split('\n'):  # pragma: no cover
            if 'has not been previously introduced' not in line and \
               'does not begin with "##gff-version"' not in line and \
               'illegal uppercase attribute "Shift"' not in line:
                print(line, file=logstream)
        assert proc.returncode == 0, 'annot cleanup command failed: %s' % cmd
        if 'annotfilter' in conf:
            os.unlink(excludefile.name)

    elif conf['source'] == 'custom':
        mod = importlib.import_module('genhub.' + conf['module'])
        mod.annotation(label, conf, workdir=workdir, logstream=logstream)

    if verify is False:  # pragma: no cover
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


def test_gdna_beebase():
    """BeeBase gDNA formatting"""

    testoutfile = 'testdata/fasta/hlab-first-6-out.fa'
    label, conf = genhub.conf.load_one('conf/test2/Hlab.yml')

    infile = 'testdata/fasta/hlab-first-6.fa.gz'
    instream = gzip.open(infile, 'rt')
    outfile = 'testdata/scratch/hlab-first-6.fa'
    outstream = open(outfile, 'w')
    gdna(label, conf, instream=instream, outstream=outstream, logstream=None,
         verify=False)
    instream.close()
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hlab gDNA formatting failed (instream --> outstream)'

    wd = 'testdata/demo-workdir'
    outstream = open(outfile, 'w')
    gdna(label, conf, workdir=wd, outstream=outstream, logstream=None,
         verify=False)
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hlab gDNA formatting failed (dir --> outstream)'

    wd = 'testdata/scratch'
    subprocess.call(['mkdir', '-p', 'testdata/scratch/Hlab'])
    instream = gzip.open(infile, 'rt')
    gdna(label, conf, workdir=wd, instream=instream, logstream=None)
    instream.close()
    outfile = 'testdata/scratch/Hlab/Hlab.gdna.fa'
    assert filecmp.cmp(testoutfile, outfile), \
        'Hlab gDNA formatting failed (instream --> dir)'


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
        'Hsal protein formatting failed (dir --> outstream)'

    wd = 'testdata/scratch'
    subprocess.call(['mkdir', '-p', 'testdata/scratch/Hsal'])
    instream = gzip.open(infile, 'rt')
    proteins(label, conf, workdir=wd, instream=instream, logstream=None)
    instream.close()
    outfile = 'testdata/scratch/Hsal/Hsal.all.prot.fa'
    assert filecmp.cmp(testoutfile, outfile), \
        'Hsal protein formatting failed (instream --> dir)'


def test_proteins_beebase():
    """BeeBase protein formatting"""

    label, conf = genhub.conf.load_one('conf/test2/Hlab.yml')
    testoutfile = 'testdata/fasta/hlab-first-20-prot-out.fa'

    infile = 'testdata/fasta/hlab-first-20-prot.fa.gz'
    instream = gzip.open(infile, 'rt')
    outfile = 'testdata/scratch/hlab-first-20-prot.fa'
    outstream = open(outfile, 'w')
    proteins(label, conf, instream=instream, outstream=outstream,
             logstream=None, verify=False)
    instream.close()
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hlab protein formatting failed (instream --> outstream)'

    wd = 'testdata/demo-workdir'
    outstream = open(outfile, 'w')
    proteins(label, conf, workdir=wd, outstream=outstream, logstream=None,
             verify=False)
    outstream.close()
    assert filecmp.cmp(testoutfile, outfile), \
        'Hlab protein formatting failed (dir --> outstream)'

    wd = 'testdata/scratch'
    subprocess.call(['mkdir', '-p', 'testdata/scratch/Hsal'])
    instream = gzip.open(infile, 'rt')
    proteins(label, conf, workdir=wd, instream=instream, logstream=None)
    instream.close()
    outfile = 'testdata/scratch/Hlab/Hlab.all.prot.fa'
    assert filecmp.cmp(testoutfile, outfile), \
        'Hlab gDNA formatting failed (instream --> dir)'


def test_annotation_ncbi():
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

    label, conf = genhub.conf.load_one('conf/test2/Ador.yml')
    annotation(label, conf, workdir='testdata/demo-workdir', logstream=None,
               verify=False)
    outfile = 'testdata/demo-workdir/Ador/Ador.gff3'
    testfile = 'testdata/gff3/ncbi-format-ador.gff3'
    assert filecmp.cmp(outfile, testfile), 'Ador annotation formatting failed'


def test_annotation_beebase():
    """BeeBase annotation formatting"""

    label, conf = genhub.conf.load_one('conf/test2/Hlab.yml')
    annotation(label, conf, workdir='testdata/demo-workdir', logstream=None,
               verify=False)
    outfile = 'testdata/demo-workdir/Hlab/Hlab.gff3'
    testfile = 'testdata/gff3/beebase-format-hlab.gff3'
    assert filecmp.cmp(outfile, testfile), 'Hlab annotation formatting failed'
