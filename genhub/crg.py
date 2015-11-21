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
Module for handling two data sets from the Centre de Regulacio Genomica.

Utilities for downloading genome assemblies, annotations, and protein
sequences from two insect genomes at the CRG.
"""

from __future__ import print_function
import sys
import genhub

crgbase = 'http://wasp.crg.eu'


def download_scaffolds(label, config, workdir='.', logstream=sys.stderr,
                       dryrun=False):
    """Download a scaffold-level genome from CRG."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'crg'
    assert 'scaffolds' in config

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download genome from CRG'
        print(logmsg, file=logstream)

    filename = config['scaffolds']
    url = '%s/%s' % (crgbase, filename)
    outfile = genhub.file_path(filename, label, workdir)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


def download_annotation(label, config, workdir='.', logstream=sys.stderr,
                        dryrun=False):
    """Download a genome annotation from CRG."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'crg'
    assert 'annotation' in config, 'Genome annotation unconfigured'

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download annotation from CRG'
        print(logmsg, file=logstream)

    filename = config['annotation']
    url = '%s/%s' % (crgbase, filename)
    outfile = genhub.file_path(filename + '.gz', label, workdir)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile, compress=True)


def download_proteins(label, config, workdir='.', logstream=sys.stderr,
                      dryrun=False):
    """Download gene model translation sequences from CRG."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'crg'
    assert 'proteins' in config

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download protein sequences from CRG'
        print(logmsg, file=logstream)

    filename = config['proteins']
    url = '%s/%s' % (crgbase, filename)
    outfile = genhub.file_path(filename, label, workdir)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds():
    """CRG scaffolds download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    testurl = 'http://wasp.crg.eu/DQUA.v01.fa.gz'
    testpath = './Dqua/DQUA.v01.fa.gz'
    testresult = (testurl, testpath)
    result = download_scaffolds(label, config, dryrun=True, logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)


def test_annot():
    """CRG annotation download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    testurl = 'http://wasp.crg.eu/DQUA.v01.gff3'
    testpath = 'CRG/Dqua/DQUA.v01.gff3.gz'
    testresult = (testurl, testpath)
    result = download_annotation(label, config, dryrun=True, workdir='CRG',
                                 logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)


def test_proteins():
    """CRG protein download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    testurl = 'http://wasp.crg.eu/DQUA.v01.pep.fa.gz'
    testpath = '/opt/db/genhub/Dqua/DQUA.v01.pep.fa.gz'
    testresult = (testurl, testpath)
    result = download_proteins(label, config, dryrun=True, logstream=None,
                               workdir='/opt/db/genhub')
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)
