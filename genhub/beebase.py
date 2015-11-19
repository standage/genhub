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
Module for handling BeeBase consortium data.

Utilities for downloading genome assemblies, annotations, and protein
sequences from the BeeBase consortium page at HymenopteraBase.
"""

from __future__ import print_function
import gzip
import subprocess
import sys
import yaml
import genhub

beebase = ('http://hymenopteragenome.org/beebase/sites/'
           'hymenopteragenome.org.beebase/files/data/consortium_data')


def download_scaffolds(label, config, workdir='.', logstream=sys.stderr,
                       dryrun=False):
    """Download a scaffold-level genome from BeeBase."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'beebase'
    assert 'scaffolds' in config

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download genome from BeeBase'
        print(logmsg, file=logstream)

    filename = config['scaffolds']
    url = '%s/%s' % (beebase, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


def download_annotation(label, config, workdir='.', logstream=sys.stderr,
                        dryrun=False):
    """Download a genome annotation from BeeBase."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'beebase'
    assert 'annotation' in config, 'Genome annotation unconfigured'

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download annotation from BeeBase'
        print(logmsg, file=logstream)

    filename = config['annotation']
    url = '%s/%s' % (beebase, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


def download_proteins(label, config, workdir='.', logstream=sys.stderr,
                      dryrun=False):
    """Download gene model translation sequences from BeeBase."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'beebase'
    assert 'proteins' in config

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download protein sequences from BeeBase'
        print(logmsg, file=logstream)

    filename = config['proteins']
    url = '%s/%s' % (beebase, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds():
    """BeeBase consortium scaffolds download"""

    label, config = genhub.conf.load_one('conf/HymHub/Emex.yml')
    testurl = ('http://hymenopteragenome.org/beebase/sites/'
               'hymenopteragenome.org.beebase/files/data/consortium_data/'
               'Eufriesea_mexicana.v1.0.fa.gz')
    testpath = './Emex/Eufriesea_mexicana.v1.0.fa.gz'
    testresult = (testurl, testpath)
    result = download_scaffolds(label, config, dryrun=True, logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)


def test_annot():
    """BeeBase consortium annotation download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dnov.yml')
    testurl = ('http://hymenopteragenome.org/beebase/sites/'
               'hymenopteragenome.org.beebase/files/data/consortium_data/'
               'Dufourea_novaeangliae_v1.1.gff.gz')
    testpath = 'BeeBase/Dnov/Dufourea_novaeangliae_v1.1.gff.gz'
    testresult = (testurl, testpath)
    result = download_annotation(label, config, dryrun=True, workdir='BeeBase',
                                 logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)


def test_proteins():
    """BeeBase consortium protein download"""

    label, config = genhub.conf.load_one('conf/HymHub/Hlab.yml')
    testurl = ('http://hymenopteragenome.org/beebase/sites/'
               'hymenopteragenome.org.beebase/files/data/consortium_data/'
               'Habropoda_laboriosa_v1.2.pep.fa.gz')
    testpath = '/opt/db/genhub/Hlab/Habropoda_laboriosa_v1.2.pep.fa.gz'
    testresult = (testurl, testpath)
    result = download_proteins(label, config, dryrun=True, logstream=None,
                               workdir='/opt/db/genhub')
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)
