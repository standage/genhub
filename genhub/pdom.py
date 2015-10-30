#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Custom handler for the *Polites dominula* genome."""

from __future__ import print_function
import filecmp
import gzip
import subprocess
import sys
import genhub

ipbase = 'http://de.iplantcollaborative.org/dl/d'


def download(label, config, workdir='.', logstream=sys.stderr):  # pragma: no cover # noqa
    download_scaffolds(label, config, workdir=workdir, logstream=logstream)
    download_annotations(label, config, workdir=workdir, logstream=logstream)
    download_proteins(label, config, workdir=workdir, logstream=logstream)


def download_scaffolds(label, config, workdir='.', logstream=sys.stderr):  # pragma: no cover # noqa
    """Download *P. dominula* scaffolds from the iPlant data store."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'custom'
    assert 'scaffolds' in config

    if logstream is not None:
        logmsg = '[GenHub: %s] download genome' % config['species']
        print(logmsg, file=logstream)

    filename = config['scaffolds']
    prefix = '53B7319E-3201-4087-9607-2D541FF34DD0'
    url = '%s/%s/%s' % (ipbase, prefix, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    genhub.download.url_download(url, outfile, follow=True)


def download_annotations(label, config, workdir='.', logstream=sys.stderr):  # pragma: no cover # noqa
    """Download *P. dominula* gene models from the iPlant data store."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'custom'
    assert 'scaffolds' in config

    if logstream is not None:
        logmsg = '[GenHub: %s] download annotation' % config['species']
        print(logmsg, file=logstream)

    filename = config['annotation']
    prefix = 'E4944CBB-7DE4-4CA1-A889-3D2A5D2E8696'
    url = '%s/%s/%s' % (ipbase, prefix, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    genhub.download.url_download(url, outfile, follow=True)


def download_proteins(label, config, workdir='.', logstream=sys.stderr):  # pragma: no cover # noqa
    """Download *P. dominula* proteins from the iPlant data store."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'custom'
    assert 'scaffolds' in config

    if logstream is not None:
        logmsg = '[GenHub: %s] download proteins' % config['species']
        print(logmsg, file=logstream)

    filename = config['proteins']
    prefix = 'ACD29139-6619-48DF-A9F2-F75CA382E248'
    url = '%s/%s/%s' % (ipbase, prefix, filename)
    outfile = '%s/%s/%s.gz' % (workdir, label, filename)
    genhub.download.url_download(url, outfile, compress=True, follow=True)


def gdna(label, conf, workdir='.', logstream=sys.stderr):
    """Decompression only, no processing required."""
    inpath = '%s/%s/%s' % (workdir, label, conf['scaffolds'])
    outpath = '%s/%s/%s.gdna.fa' % (workdir, label, label)
    with gzip.open(inpath, 'rt') as infile, open(outpath, 'w') as outfile:
        for line in infile:
            print(line, end='', file=outfile)


def proteins(label, conf, workdir='.', logstream=sys.stderr):
    """Decompression only, no processing required."""
    inpath = '%s/%s/%s.gz' % (workdir, label, conf['proteins'])
    outpath = '%s/%s/%s.all.prot.fa' % (workdir, label, label)
    with gzip.open(inpath, 'rt') as infile, open(outpath, 'w') as outfile:
        for line in infile:
            print(line, end='', file=outfile)


def annotation(label, conf, workdir='.', logstream=sys.stderr):
    """Preprocess annotations"""
    inpath = '%s/%s/%s' % (workdir, label, conf['annotation'])
    outpath = '%s/%s/%s.gff3' % (workdir, label, label)
    command = 'genhub-format-gff3.py --outfile %s %s' % (outpath, inpath)
    subprocess.check_call(command.split(' '))


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_format():
    """Pdom formatting task"""

    label, conf = genhub.conf.load_one('conf/Pdom-ut.yml')
    wd = 'testdata/demo-workdir'
    genhub.format.gdna(label, conf, workdir=wd, logstream=None)
    genhub.format.proteins(label, conf, workdir=wd, logstream=None)
    genhub.format.annotation(label, conf, workdir=wd, logstream=None)
