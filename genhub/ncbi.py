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


class NcbiDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(NcbiDB, self).__init__(label, conf, workdir)

        assert self.config['source'] == 'ncbi'
        assert 'branch' in self.config
        assert 'species' in self.config
        assert 'accession' in self.config
        assert 'build' in self.config

        species = self.config['species'].replace(' ', '_')
        self.acc = self.config['accession'] + '_' + self.config['build']

        base = 'ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq'
        url_parts = [base, self.config['branch'], species,
                     'all_assembly_versions', self.acc]
        self.specbase = '/'.join(url_parts + [self.acc])
        print('DEBUG: %s' % self.specbase, file=sys.stderr)
        self.format_gdna = self.format_fasta
        self.format_prot = self.format_fasta

    def __repr__(self):
        return 'NCBI'

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
            if line.startswith('>'):
                pattern = '>gi\|\d+\|(ref|gb)\|([^\|]+)\S+'
                line = re.sub(pattern, '>\g<2>', line)
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('gunzip -c %s' % self.gff3path)
        if 'annotfilter' in self.config:
            excludefile = genhub.conf.conf_filter_file(self.config)
            cmds.append('grep -vf %s' % excludefile.name)
        cmds.append('tidygff3')
        cmds.append('genhub-format-gff3.py --source ncbi -')
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
               line != '':
                print(line, file=logstream)
        assert proc.returncode == 0, \
            'annot cleanup command failed: %s' % commands
        if 'annotfilter' in self.config:
            os.unlink(excludefile.name)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds_download():
    """NCBI scaffolds download"""

    label, config = genhub.conf.load_one('conf/test/Emon.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_monoceros/CHR_Un/'
               'emon_ref_3.4_chrUn.fa.gz')
    testpath = './Emon/emon_ref_3.4_chrUn.fa.gz'
    emon_db = NcbiDB(label, config)
    assert emon_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (emon_db.gdnaurl, testurl)
    assert emon_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (emon_db.gdnapath, testpath)

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/CHR_Un/'
               'bv_ref_1.1_chrUn.fa.gz')
    testpath = '/some/path/Bvul/bv_ref_1.1_chrUn.fa.gz'
    bvul_db = NcbiDB(label, config, workdir='/some/path')
    assert bvul_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (bvul_db.gdnaurl, testurl)
    assert bvul_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (bvul_db.gdnapath, testpath)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/CHR_Un/'
               'ado_ref_Apis_dorsata_1.3_chrUn.fa.gz')
    testpath = './Ador/ado_ref_Apis_dorsata_1.3_chrUn.fa.gz'
    ador_db = NcbiDB(label, config)
    assert '%r' % ador_db == 'NCBI'
    assert ador_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (ador_db.gdnaurl, testurl)
    assert ador_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (ador_db.gdnapath, testpath)
    assert ador_db.compress_gdna is False


def test_chromosomes_download():
    """NCBI chromosome download"""

    label, config = genhub.conf.load_one('conf/test/Docc.yml')
    urls = ['docc_ref_1.6_1.fa.gz', 'docc_ref_1.6_2.fa.gz',
            'docc_ref_1.6_3.fa.gz', 'docc_ref_1.6_4.fa.gz',
            'docc_ref_1.6_5.fa.gz', 'docc_ref_1.6_6.fa.gz',
            'docc_ref_1.6_7.fa.gz', 'docc_ref_1.6_8.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Draconis_occidentalis/'
              'Assembled_chromosomes/seq/')
    testurls = [prefix + x for x in urls]
    testpath = './Docc/Docc.orig.fa.gz'
    docc_db = NcbiDB(label, config)
    assert docc_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (docc_db.gdnaurl, testurls)
    assert docc_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (docc_db.gdnapath, chrmpath)

    label, config = genhub.conf.load_one('conf/test/Epeg.yml')
    urls = ['epeg_reg_Epe_2.1_01.fa.gz', 'epeg_reg_Epe_2.1_02.fa.gz',
            'epeg_reg_Epe_2.1_03.fa.gz', 'epeg_reg_Epe_2.1_04.fa.gz',
            'epeg_reg_Epe_2.1_05.fa.gz', 'epeg_reg_Epe_2.1_06.fa.gz',
            'epeg_reg_Epe_2.1_07.fa.gz', 'epeg_reg_Epe_2.1_08.fa.gz',
            'epeg_reg_Epe_2.1_09.fa.gz', 'epeg_reg_Epe_2.1_10.fa.gz',
            'epeg_reg_Epe_2.1_11.fa.gz', 'epeg_reg_Epe_2.1_12.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_pegasus/'
              'Assembled_chromosomes/seq/')
    testurls = [prefix + x for x in urls]
    testpath = './Epeg/Epeg.orig.fa.gz'
    epeg_db = NcbiDB(label, config)
    assert epeg_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (epeg_db.gdnaurl, testurls)
    assert epeg_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (epeg_db.gdnapath, chrmpath)

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
    testurls = [prefix + x for x in urls]
    testpath = '/home/student/data/Amel/Amel.orig.fa.gz'
    amel_db = NcbiDB(label, config, workdir='/home/student/data')
    assert amel_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (amel_db.gdnaurl, testurls)
    assert amel_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (amel_db.gdnapath, chrmpath)


def test_annot_download():
    """NCBI annotation download"""

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/GFF/'
               'ref_Basiliscus_vulgaris_1.1_top_level.gff3.gz')
    testpath = ('/another/path//Bvul/'
                'ref_Basiliscus_vulgaris_1.1_top_level.gff3.gz')
    bvul_db = NcbiDB(label, config, workdir='/another/path/')
    assert bvul_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (bvul_db.gff3url, testurl)
    assert bvul_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (bvul_db.gff3path, testpath)

    label, config = genhub.conf.load_one('conf/test/Epeg.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_pegasus/GFF/'
               'ref_EPEG_2.1_top_level.gff3.gz')
    testpath = './Epeg/ref_EPEG_2.1_top_level.gff3.gz'
    epeg_db = NcbiDB(label, config)
    assert epeg_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (epeg_db.gff3url, testurl)
    assert epeg_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (epeg_db.gff3path, testpath)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/GFF/'
               'ref_Apis_dorsata_1.3_top_level.gff3.gz')
    testpath = './Ador/ref_Apis_dorsata_1.3_top_level.gff3.gz'
    ador_db = NcbiDB(label, config)
    assert ador_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (ador_db.gff3url, testurl)
    assert ador_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (ador_db.gff3path, testpath)
    assert ador_db.compress_gff3 is False


def test_proteins_download():
    """NCBI protein download"""

    label, config = genhub.conf.load_one('conf/test/Emon.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_monoceros/protein/'
               'protein.fa.gz')
    testpath = './Emon/protein.fa.gz'
    emon_db = NcbiDB(label, config)
    assert emon_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (emon_db.proturl, testurl)
    assert emon_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (emon_db.protpath, testpath)

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/protein/'
               'protein.fa.gz')
    testpath = './Bvul/protein.fa.gz'
    bvul_db = NcbiDB(label, config)
    assert bvul_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (bvul_db.proturl, testurl)
    assert bvul_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (bvul_db.protpath, testpath)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/protein/'
               'protein.fa.gz')
    testpath = '/home/gandalf/HymHub/Ador/protein.fa.gz'
    ador_db = NcbiDB(label, config, workdir='/home/gandalf/HymHub')
    assert ador_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (ador_db.proturl, testurl)
    assert ador_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (ador_db.protpath, testpath)
    assert ador_db.compress_prot is False


def test_gdna_format():
    """NCBI gDNA formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hsal.yml')
    hsal_db = NcbiDB(label, conf, workdir='testdata/demo-workdir')
    hsal_db.preprocess_gdna(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hsal/Hsal.gdna.fa'
    testoutfile = 'testdata/fasta/hsal-first-7-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Hsal gDNA formatting failed'

    label, conf = genhub.conf.load_one('conf/HymHub/Tcas.yml')
    tcas_db = NcbiDB(label, conf, workdir='testdata/demo-workdir')
    tcas_db.preprocess_gdna(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Tcas/Tcas.gdna.fa'
    testoutfile = 'testdata/fasta/tcas-first-33-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Tcas gDNA formatting failed'


def test_annot_format():
    """NCBI annotation formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Aech.yml')
    aech_db = NcbiDB(label, conf, workdir='testdata/demo-workdir')
    aech_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Aech/Aech.gff3'
    testfile = 'testdata/gff3/ncbi-format-aech.gff3'
    assert filecmp.cmp(outfile, testfile), 'Aech annotation formatting failed'

    label, conf = genhub.conf.load_one('conf/HymHub/Pbar.yml')
    conf['annotfilter'] = 'NW_011933506.1'
    pbar_db = NcbiDB(label, conf, workdir='testdata/demo-workdir')
    pbar_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Pbar/Pbar.gff3'
    testfile = 'testdata/gff3/ncbi-format-pbar.gff3'
    assert filecmp.cmp(outfile, testfile), 'Pbar annotation formatting failed'

    label, conf = genhub.conf.load_one('conf/HymHub/Ador.yml')
    conf['annotfilter'] = ['NW_006264094.1', 'NW_006263516.1']
    ador_db = NcbiDB(label, conf, workdir='testdata/demo-workdir')
    ador_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Ador/Ador.gff3'
    testfile = 'testdata/gff3/ncbi-format-ador.gff3'
    assert filecmp.cmp(outfile, testfile), 'Ador annotation formatting failed'


def test_prot_ncbi():
    """NCBI protein formatting"""

    label, conf = genhub.conf.load_one('conf/HymHub/Hsal.yml')
    hsal_db = NcbiDB(label, conf, workdir='testdata/demo-workdir')
    hsal_db.preprocess_prot(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Hsal/Hsal.all.prot.fa'
    testoutfile = 'testdata/fasta/hsal-13-prot-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Hsal protein formatting failed'
