#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Module for handling FlyBase data hosted at NCBI."""

from __future__ import print_function
import gzip
import os
import subprocess
import sys
import yaml
import genhub

ncbibase = ('ftp://ftp.ncbi.nih.gov/genomes/'
            'Drosophila_melanogaster/RELEASE_5_48')


def download_chromosomes(label, config, workdir='.', logstream=sys.stderr,
                         dryrun=False):
    """Download a chromosome-level genome from NCBI."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi_flybase'
    assert 'accessions' in config

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] download genome from NCBI' % config['species']
        print(logmsg, file=logstream)

    urls = ['%s/%s.fna' % (ncbibase, acc) for acc in config['accessions']]
    outfile = '%s/%s/%s.orig.fa.gz' % (workdir, label, label)
    if dryrun is True:
        return urls, outfile
    else:  # pragma: no cover
        genhub.download.url_download(urls, outfile, compress=True)


def download_annotation(label, config, workdir='.', logstream=sys.stderr,
                        dryrun=False):
    """Download a genome annotation from NCBI."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi_flybase'
    assert 'accessions' in config
    assert 'annotation' in config, 'Genome annotation unconfigured'

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download annotation from NCBI'
        print(logmsg, file=logstream)

    urls = ['%s/%s.gff' % (ncbibase, acc) for acc in config['accessions']]
    filename = config['annotation']
    outfile = '%s/%s/%s' % (workdir, label, filename)
    if dryrun is True:
        return urls, outfile
    else:  # pragma: no cover
        command = ['gt', 'gff3', '-sort', '-tidy', '-force', '-gzip',
                   '-o', '%s' % outfile]
        for url, acc in zip(urls, config['accessions']):
            tempdir = '%s/%s' % (workdir, label)
            tempout = '%s/%s.gff.gz' % (tempdir, os.path.basename(acc))
            genhub.download.url_download(url, tempout, compress=True)
            command.append(tempout)
        logfile = open('%s.log' % outfile, 'w')
        proc = subprocess.Popen(command, stderr=subprocess.PIPE)
        proc.wait()
        for line in proc.stderr:
            print(line, end='', file=logfile)
        assert proc.returncode == 0, ('command failed, check the log (%s.log):'
                                      '%s' % (outfile, ' '.join(command)))


def download_proteins(label, config, workdir='.', logstream=sys.stderr,
                      dryrun=False):
    """Download gene model translation sequences from NCBI."""
    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi_flybase'
    assert 'accessions' in config

    if logstream is not None:  # pragma: no cover
        logmsg = '[GenHub: %s] download genome from NCBI' % config['species']
        print(logmsg, file=logstream)

    urls = ['%s/%s.faa' % (ncbibase, acc) for acc in config['accessions']]
    outfile = '%s/%s/protein.fa.gz' % (workdir, label)
    if dryrun is True:
        return urls, outfile
    else:  # pragma: no cover
        genhub.download.url_download(urls, outfile, compress=True)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_chromosomes():
    """NCBI/FlyBase chromosome download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    urls = ['ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_X/NC_004354.fna',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_2/NT_033778.fna',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_2/NT_033779.fna',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_3/NT_033777.fna',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_3/NT_037436.fna',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_4/NC_004353.fna']
    test = (urls, './Dmel/Dmel.orig.fa.gz')
    result = download_chromosomes(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)


def test_annot():
    """NCBI/FlyBase annotation download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    urls = ['ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_X/NC_004354.gff',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_2/NT_033778.gff',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_2/NT_033779.gff',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_3/NT_033777.gff',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_3/NT_037436.gff',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_4/NC_004353.gff']
    test = (urls, './Dmel/dmel-5.48-ncbi.gff3.gz')
    result = download_annotation(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)


def test_proteins():
    """NCBI/FlyBase protein download"""
    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    urls = ['ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_X/NC_004354.faa',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_2/NT_033778.faa',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_2/NT_033779.faa',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_3/NT_033777.faa',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_3/NT_037436.faa',
            'ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
            'RELEASE_5_48/CHR_4/NC_004353.faa']
    test = (urls, './Dmel/protein.fa.gz')
    result = download_proteins(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)
