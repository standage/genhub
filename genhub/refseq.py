#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Genome database implementation for data from NCBI."""

from __future__ import print_function
import filecmp
import gzip
import os
import re
import subprocess
import sys
import genhub


class RefSeqDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(RefSeqDB, self).__init__(label, conf, workdir)

        assert self.config['source'] == 'refseq'
        assert 'branch' in self.config
        assert 'species' in self.config
        assert 'accession' in self.config
        assert 'build' in self.config

        species = self.config['species'].replace(' ', '_')
        species = species.replace('(', '')
        species = species.replace(')', '')
        self.acc = self.config['accession'] + '_' + self.config['build']

        base = 'ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq'
        url_parts = [base, self.config['branch'], species,
                     'all_assembly_versions', self.acc]
        self.specbase = '/'.join(url_parts + [self.acc])
        self.format_gdna = self.format_fasta
        self.format_prot = self.format_fasta

    def __repr__(self):
        return 'RefSeq'

    @property
    def gdnafilename(self):
        return '%s_genomic.fna.gz' % self.acc

    @property
    def gff3filename(self):
        return '%s_genomic.gff.gz' % self.acc

    @property
    def protfilename(self):
        return '%s_protein.faa.gz' % self.acc

    @property
    def gdnaurl(self):
        return '%s_genomic.fna.gz' % self.specbase

    @property
    def gff3url(self):
        return '%s_genomic.gff.gz' % self.specbase

    @property
    def proturl(self):
        return '%s_protein.faa.gz' % self.specbase

    def format_fasta(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            # No processing required since new RefSeq migration (2015-11-30).
            # If any is ever needed again, do it here.
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('gunzip -c %s' % self.gff3path)
        if 'annotfilter' in self.config:
            excludefile = genhub.conf.conf_filter_file(self.config)
            cmds.append('grep -vf %s' % excludefile.name)
        cmds.append('tidygff3')
        cmds.append('genhub-format-gff3.py --source refseq -')
        cmds.append('gt gff3 -sort -tidy -o %s -force' % self.gff3file)

        commands = ' | '.join(cmds)
        if debug:  # pragma: no cover
            print('DEBUG: running command: %s' % commands, file=logstream)
        proc = subprocess.Popen(commands, shell=True, universal_newlines=True,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        for line in stderr.split('\n'):  # pragma: no cover
            if 'has not been previously introduced' not in line and \
               'does not begin with "##gff-version"' not in line and \
               'more than one pseudogene attribute' not in line and \
               line != '':
                print(line, file=logstream)
        assert proc.returncode == 0, \
            'annot cleanup command failed: %s' % commands
        if 'annotfilter' in self.config:
            os.unlink(excludefile.name)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_genome_download():
    """RefSeq chromosomes/scaffolds download"""

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/invertebrate/'
               'Apis_dorsata/all_assembly_versions/'
               'GCF_000469605.1_Apis_dorsata_1.3/'
               'GCF_000469605.1_Apis_dorsata_1.3_genomic.fna.gz')
    testpath = './Ador/GCF_000469605.1_Apis_dorsata_1.3_genomic.fna.gz'
    ador_db = RefSeqDB(label, config)
    assert '%r' % ador_db == 'RefSeq'
    assert ador_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (ador_db.gdnaurl, testurl)
    assert ador_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (ador_db.gdnapath, testpath)
    assert ador_db.compress_gdna is False

    label, config = genhub.conf.load_one('conf/HymHub/Amel.yml')
    testurl = ('ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/invertebrate/'
               'Apis_mellifera/all_assembly_versions/'
               'GCF_000002195.4_Amel_4.5/'
               'GCF_000002195.4_Amel_4.5_genomic.fna.gz')
    testpath = './Amel/GCF_000002195.4_Amel_4.5_genomic.fna.gz'
    amel_db = RefSeqDB(label, config)
    assert amel_db.gdnaurl == testurl, \
        'chromosome URL mismatch\n%s\n%s' % (amel_db.gdnaurl, testurl)
    assert amel_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (amel_db.gdnapath, testpath)
    assert ador_db.compress_gdna is False


def test_annot_download():

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/invertebrate/'
               'Apis_dorsata/all_assembly_versions/'
               'GCF_000469605.1_Apis_dorsata_1.3/'
               'GCF_000469605.1_Apis_dorsata_1.3_genomic.gff.gz')
    testpath = './Ador/GCF_000469605.1_Apis_dorsata_1.3_genomic.gff.gz'
    ador_db = RefSeqDB(label, config)
    assert ador_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (ador_db.gff3url, testurl)
    assert ador_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (ador_db.gff3path, testpath)
    assert ador_db.compress_gff3 is False


def test_proteins_download():
    """RefSeq protein download"""

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/invertebrate/'
               'Apis_dorsata/all_assembly_versions/'
               'GCF_000469605.1_Apis_dorsata_1.3/'
               'GCF_000469605.1_Apis_dorsata_1.3_protein.faa.gz')
    testpath = ('/home/gandalf/HymHub/Ador/'
                'GCF_000469605.1_Apis_dorsata_1.3_protein.faa.gz')
    ador_db = RefSeqDB(label, config, workdir='/home/gandalf/HymHub')
    assert ador_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (ador_db.proturl, testurl)
    assert ador_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (ador_db.protpath, testpath)
    assert ador_db.compress_prot is False


def test_gdna_format():
    """RefSeq gDNA formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hsal.yml')
    hsal_db = RefSeqDB(label, conf, workdir='testdata/demo-workdir')
    hsal_db.preprocess_gdna(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hsal/Hsal.gdna.fa'
    testoutfile = 'testdata/fasta/hsal-first-7-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Hsal gDNA formatting failed'

    label, conf = genhub.conf.load_one('conf/HymHub/Tcas.yml')
    tcas_db = RefSeqDB(label, conf, workdir='testdata/demo-workdir')
    tcas_db.preprocess_gdna(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Tcas/Tcas.gdna.fa'
    testoutfile = 'testdata/fasta/tcas-first-33-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Tcas gDNA formatting failed'


def test_annot_format():
    """RefSeq annotation formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Aech.yml')
    aech_db = RefSeqDB(label, conf, workdir='testdata/demo-workdir')
    aech_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Aech/Aech.gff3'
    testfile = 'testdata/gff3/ncbi-format-aech.gff3'
    assert filecmp.cmp(outfile, testfile), 'Aech annotation formatting failed'

    label, conf = genhub.conf.load_one('conf/HymHub/Pbar.yml')
    conf['annotfilter'] = 'NW_011933506.1'
    pbar_db = RefSeqDB(label, conf, workdir='testdata/demo-workdir')
    pbar_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Pbar/Pbar.gff3'
    testfile = 'testdata/gff3/ncbi-format-pbar.gff3'
    assert filecmp.cmp(outfile, testfile), 'Pbar annotation formatting failed'

    label, conf = genhub.conf.load_one('conf/HymHub/Ador.yml')
    conf['annotfilter'] = ['NW_006264094.1', 'NW_006263516.1']
    ador_db = RefSeqDB(label, conf, workdir='testdata/demo-workdir')
    ador_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Ador/Ador.gff3'
    testfile = 'testdata/gff3/ncbi-format-ador.gff3'
    assert filecmp.cmp(outfile, testfile), 'Ador annotation formatting failed'


def test_prot_ncbi():
    """RefSeq protein formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hsal.yml')
    hsal_db = RefSeqDB(label, conf, workdir='testdata/demo-workdir')
    hsal_db.preprocess_prot(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hsal/Hsal.all.prot.fa'
    testoutfile = 'testdata/fasta/hsal-13-prot-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Hsal protein formatting failed'