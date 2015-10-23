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
Module for handling NCBI data.

Utilities for downloading genome assemblies, annotations, and protein
sequences from NCBI's FTP site.
"""

from __future__ import print_function
import gzip
import subprocess
import sys
import yaml
import genhub

ncbibase = 'ftp://ftp.ncbi.nih.gov/genomes'


def download_chromosomes(label, config, workdir='.', logstream=sys.stderr,
                         dryrun=False):
    """Download a chromosome-level genome from NCBI."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi'
    assert 'chromosomes' in config and 'scaffolds' not in config, \
        'Must configure only chromosomes or scaffolds, not both'

    if logstream is not None:  # pragma: nocover
        logmsg = '[GenHub: %s] download genome from NCBI' % config['species']
        print(logmsg, file=logstream)

    urls = list()
    species = config['species'].replace(' ', '_')
    prefix = config['prefix']
    for remotefile in config['chromosomes']:
        url = '%s/%s/%s/%s' % (ncbibase, species, prefix, remotefile)
        urls.append(url)
    outfile = '%s/%s/%s.orig.fa.gz' % (workdir, label, label)
    if dryrun is True:
        return urls, outfile
    else:  # pragma: no cover
        genhub.download.url_download(urls, outfile)


def download_scaffolds(label, config, workdir='.', logstream=sys.stderr,
                       dryrun=False):
    """Download a scaffold-level genome from NCBI."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi'
    assert 'chromosomes' not in config and 'scaffolds' in config, \
        'Must configure only chromosomes or scaffolds, not both'

    if logstream is not None:  # pragma: nocover
        logmsg = '[GenHub: %s] download genome from NCBI' % config['species']
        print(logmsg, file=logstream)

    species = config['species'].replace(' ', '_')
    filename = config['scaffolds']
    url = '%s/%s/CHR_Un/%s' % (ncbibase, species, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


def download_annotation(label, config, workdir='.', logstream=sys.stderr,
                        dryrun=False):
    """Download a genome annotation from NCBI."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi'
    assert 'annotation' in config, 'Genome annotation unconfigured'

    if logstream is not None:  # pragma: nocover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download annotation from NCBI'
        print(logmsg, file=logstream)

    species = config['species'].replace(' ', '_')
    filename = config['annotation']
    url = '%s/%s/GFF/%s' % (ncbibase, species, filename)
    outfile = '%s/%s/%s' % (workdir, label, filename)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


def download_proteins(label, config, workdir='.', logstream=sys.stderr,
                      dryrun=False):
    """Download gene model translation sequences from NCBI."""

    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi'

    if logstream is not None:  # pragma: nocover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download protein sequences from NCBI'
        print(logmsg, file=logstream)

    species = config['species'].replace(' ', '_')
    url = '%s/%s/protein/protein.fa.gz' % (ncbibase, species)
    outfile = '%s/%s/protein.fa.gz' % (workdir, label)
    if dryrun is True:
        return url, outfile
    else:  # pragma: no cover
        genhub.download.url_download(url, outfile)


def download_flybase(label, config, workdir='.', logstream=sys.stderr,
                     dryrun=False):
    """
    Download Drosophila data from NCBI.

    Genome sequences and annotations for Drosophila melanogaster in NCBI are
    organized differently than for most other species, presumably since they
    are sourced from FlyBase. This function downloads all of the genome
    sequences, annotations, and protein sequences for Dmel.
    """
    assert 'source' in config, 'Data source unconfigured'
    assert config['source'] == 'ncbi_flybase'

    if logstream is not None:  # pragma: nocover
        logmsg = '[GenHub: %s] ' % config['species']
        logmsg += 'download genome data from NCBI'
        print(logmsg, file=logstream)

    species = config['species'].replace(' ', '_')
    chrs, anns, tmps, prts = list(), list(), list(), list()
    chrout = '%s/%s/%s.orig.fa.gz' % (workdir, label, label)
    prtout = '%s/%s/protein.fa.gz' % (workdir, label)
    annout = '%s/%s/%s' % (workdir, label, config['annotation'])
    for acc in config['accessions']:
        base = '%s/%s/%s/%s' % (ncbibase, species, config['prefix'], acc)
        chrs.append(base + '.fna')
        prts.append(base + '.faa')
        anns.append(base + '.gff')
        tmps.append('%s/%s/%s.gff.gz' % (workdir, label,
                    acc.split('/')[1]))
    if dryrun is True:
        return (chrs, anns, prts, chrout, annout, prtout)
    else:  # pragma: no cover
        genhub.download.url_download(chrs, chrout, compress=True)
        genhub.download.url_download(prts, prtout, compress=True)
        for annremote, annlocal in zip(anns, tmps):
            genhub.download.url_download(annremote, annlocal, compress=True)

        with gzip.open(annout, 'wb') as outfile:
            cmd = 'gt gff3 -sort -tidy ' + ' '.join(tmps)
            proc = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
            for line in proc.stdout:
                outfile.write(line)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds():
    """NCBI scaffolds download"""

    label, config = genhub.conf.load_one('conf/test/Emon.yml')
    testscaf = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_monoceros/CHR_Un/'
                'emon_ref_3.4_chrUn.fa.gz')
    testann = './Emon/emon_ref_3.4_chrUn.fa.gz'
    testresult = (testscaf, testann)
    result = download_scaffolds(label, config, dryrun=True, logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testscaf = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/CHR_Un/'
                'bv_ref_1.1_chrUn.fa.gz')
    testann = '/some/path/Bvul/bv_ref_1.1_chrUn.fa.gz'
    testresult = (testscaf, testann)
    result = download_scaffolds(label, config, workdir='/some/path',
                                dryrun=True, logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testscaf = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/CHR_Un/'
                'ado_ref_Apis_dorsata_1.3_chrUn.fa.gz')
    testann = './Ador/ado_ref_Apis_dorsata_1.3_chrUn.fa.gz'
    testresult = (testscaf, testann)
    result = download_scaffolds(label, config, dryrun=True, logstream=None)
    assert result == testresult, \
        'filenames do not match\n%s\n%s\n' % (result, testresult)


def test_chromosomes():
    """NCBI chromosome download"""

    label, config = genhub.conf.load_one('conf/test/Docc.yml')
    urls = ['docc_ref_1.6_1.fa.gz', 'docc_ref_1.6_2.fa.gz',
            'docc_ref_1.6_3.fa.gz', 'docc_ref_1.6_4.fa.gz',
            'docc_ref_1.6_5.fa.gz', 'docc_ref_1.6_6.fa.gz',
            'docc_ref_1.6_7.fa.gz', 'docc_ref_1.6_8.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Draconis_occidentalis/'
              'Assembled_chromosomes/seq/')
    urls = [prefix + x for x in urls]
    test = (urls, './Docc/Docc.orig.fa.gz')
    result = download_chromosomes(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)

    label, config = genhub.conf.load_one('conf/test/Epeg.yml')
    urls = ['epeg_reg_Epe_2.1_01.fa.gz', 'epeg_reg_Epe_2.1_02.fa.gz',
            'epeg_reg_Epe_2.1_03.fa.gz', 'epeg_reg_Epe_2.1_04.fa.gz',
            'epeg_reg_Epe_2.1_05.fa.gz', 'epeg_reg_Epe_2.1_06.fa.gz',
            'epeg_reg_Epe_2.1_07.fa.gz', 'epeg_reg_Epe_2.1_08.fa.gz',
            'epeg_reg_Epe_2.1_09.fa.gz', 'epeg_reg_Epe_2.1_10.fa.gz',
            'epeg_reg_Epe_2.1_11.fa.gz', 'epeg_reg_Epe_2.1_12.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_pegasus/'
              'Assembled_chromosomes/seq/')
    urls = [prefix + x for x in urls]
    test = (urls, './Epeg/Epeg.orig.fa.gz')
    result = download_chromosomes(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)

    label, config = genhub.conf.load_one('conf/HymHub/Amel.yml')
    urls = ['ame_ref_Amel_4.5_unplaced.fa.gz', 'ame_ref_Amel_4.5_chrLG1.fa.gz',
            'ame_ref_Amel_4.5_chrLG2.fa.gz', 'ame_ref_Amel_4.5_chrLG3.fa.gz',
            'ame_ref_Amel_4.5_chrLG4.fa.gz', 'ame_ref_Amel_4.5_chrLG5.fa.gz',
            'ame_ref_Amel_4.5_chrLG6.fa.gz', 'ame_ref_Amel_4.5_chrLG7.fa.gz',
            'ame_ref_Amel_4.5_chrLG8.fa.gz', 'ame_ref_Amel_4.5_chrLG9.fa.gz',
            'ame_ref_Amel_4.5_chrLG10.fa.gz', 'ame_ref_Amel_4.5_chrLG11.fa.gz',
            'ame_ref_Amel_4.5_chrLG12.fa.gz', 'ame_ref_Amel_4.5_chrLG13.fa.gz',
            'ame_ref_Amel_4.5_chrLG14.fa.gz', 'ame_ref_Amel_4.5_chrLG15.fa.gz',
            'ame_ref_Amel_4.5_chrLG16.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_mellifera/'
              'Assembled_chromosomes/seq/')
    urls = [prefix + x for x in urls]
    test = (urls, '/home/student/data/Amel/Amel.orig.fa.gz')
    result = download_chromosomes(label, config, workdir='/home/student/data',
                                  dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)


def test_annot():
    """NCBI annotation download"""

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/GFF/'
               'ref_Basiliscus_vulgaris_1.1_top_level.gff3.gz')
    testfile = ('/another/path//Bvul/'
                'ref_Basiliscus_vulgaris_1.1_top_level.gff3.gz')
    test = (testurl, testfile)
    result = download_annotation(label, config, workdir='/another/path/',
                                 dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)

    label, config = genhub.conf.load_one('conf/test/Epeg.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_pegasus/GFF/'
               'ref_EPEG_2.1_top_level.gff3.gz')
    testfile = './Epeg/ref_EPEG_2.1_top_level.gff3.gz'
    test = (testurl, testfile)
    result = download_annotation(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/GFF/'
               'ref_Apis_dorsata_1.3_top_level.gff3.gz')
    testfile = './Ador/ref_Apis_dorsata_1.3_top_level.gff3.gz'
    test = (testurl, testfile)
    result = download_annotation(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)


def test_proteins():
    """NCBI protein download"""

    label, config = genhub.conf.load_one('conf/test/Emon.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_monoceros/protein/'
               'protein.fa.gz')
    testfile = './Emon/protein.fa.gz'
    test = (testurl, testfile)
    result = download_proteins(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/protein/'
               'protein.fa.gz')
    testfile = './Bvul/protein.fa.gz'
    test = (testurl, testfile)
    result = download_proteins(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/protein/'
               'protein.fa.gz')
    testfile = '/home/gandalf/HymHub/Ador/protein.fa.gz'
    test = (testurl, testfile)
    result = download_proteins(label, config, workdir='/home/gandalf/HymHub',
                               dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)


def test_flybase():
    """NCBI FlyBase data download"""

    label, config = genhub.conf.load_one('conf/HymHub/Dmel.yml')
    bases = ['CHR_X/NC_004354', 'CHR_2/NT_033778', 'CHR_2/NT_033779',
             'CHR_3/NT_033777', 'CHR_3/NT_037436', 'CHR_4/NC_004353']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Drosophila_melanogaster/'
              'RELEASE_5_48/')
    chrs = [prefix + x + '.fna' for x in bases]
    anns = [prefix + x + '.gff' for x in bases]
    prts = [prefix + x + '.faa' for x in bases]
    test = (chrs, anns, prts, './Dmel/Dmel.orig.fa.gz',
            './Dmel/dmel-5.48-ncbi.gff3.gz',
            './Dmel/protein.fa.gz')
    result = download_flybase(label, config, dryrun=True, logstream=None)
    assert result == test, 'filenames do not match\n%s\n%s\n' % (result, test)
