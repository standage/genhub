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
import os
import subprocess
import sys
import genhub


class FlyBaseDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(FlyBaseDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'ncbi_flybase'
        assert 'species' in self.config
        species = self.config['species'].replace(' ', '_')
        self.specbase = ('ftp://ftp.ncbi.nih.gov/genomes/'
                         'Drosophila_melanogaster/RELEASE_5_48')

    def __repr__(self):
        return 'FlyBase@NCBI'

    @property
    def gdnafilename(self):
        return '%s.orig.fa.gz' % self.label

    @property
    def gdnaurl(self):
        urls = list()
        for acc in self.config['accessions']:
            url = '%s/%s.fna' % (self.specbase, acc)
            urls.append(url)
        return urls

    @property
    def gff3url(self):
        urls = list()
        for acc in self.config['accessions']:
            url = '%s/%s.gff' % (self.specbase, acc)
            urls.append(url)
        return urls

    @property
    def proturl(self):
        urls = list()
        for acc in self.config['accessions']:
            url = '%s/%s.faa' % (self.specbase, acc)
            urls.append(url)
        return urls

    def download_gff3(self, logstream=sys.stderr):  # pragma: no cover
        """Override the default download task."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download genome annotation from %r' % self
            print(logmsg, file=logstream)

        command = ['gt', 'gff3', '-sort', '-tidy', '-force', '-gzip', '-o',
                   '%s' % self.gff3path]
        for url, acc in zip(self.gff3url, self.config['accessions']):
            tempout = '%s/%s.gff.gz' % (self.dbdir, os.path.basename(acc))
            genhub.download.url_download(url, tempout, compress=True)
            command.append(tempout)
        logfile = open('%s.log' % self.gff3path, 'w')
        proc = subprocess.Popen(command, stderr=subprocess.PIPE)
        proc.wait()
        for line in proc.stderr:
            print(line, end='', file=logfile)
        assert proc.returncode == 0, ('command failed, check the log '
                                      '(%s.log): %s' %
                                      (self.gff3path, ' '.join(command)))


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_chromosomes():
    """NCBI/FlyBase chromosome download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    testurls = ['ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
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
    testpath = './Dmel/Dmel.orig.fa.gz'
    dmel_db = FlyBaseDB(label, config)
    assert dmel_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (dmel_db.gdnaurl, testurls)
    print('DEBUG: ' + dmel_db.gdnafilename, file=sys.stderr)
    assert dmel_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (dmel_db.gdnapath, testpath)
    assert '%r' % dmel_db == 'FlyBase@NCBI'
    assert dmel_db.compress_gdna is True


def test_annot():
    """NCBI/FlyBase annotation download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    testurls = ['ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
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
    testpath = './Dmel/dmel-5.48-ncbi.gff3.gz'
    dmel_db = FlyBaseDB(label, config)
    assert dmel_db.gff3url == testurls, \
        'annotation URL mismatch\n%s\n%s' % (dmel_db.gff3url, testurls)
    assert dmel_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (dmel_db.gff3path, testpath)
    assert dmel_db.compress_gff3 is True


def test_proteins():
    """NCBI/FlyBase protein download"""
    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    testurls = ['ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
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
    testpath = './Dmel/protein.fa.gz'
    dmel_db = FlyBaseDB(label, config)
    assert dmel_db.proturl == testurls, \
        'protein URL mismatch\n%s\n%s' % (dmel_db.proturl, testurls)
    assert dmel_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (dmel_db.protpath, testpath)
    assert dmel_db.compress_prot is True
