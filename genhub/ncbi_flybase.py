#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Genome database implementation for FlyBase data at NCBI."""

from __future__ import print_function
import filecmp
import gzip
import os
import re
import subprocess
import sys
import genhub


class FlyBaseDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(FlyBaseDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'ncbi_flybase'
        assert 'species' in self.config
        species = self.config['species'].replace(' ', '_')
        self.specbase = ('ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                         'Drosophila_melanogaster/RELEASE_5_48')
        self.format_gdna = self.format_fasta
        self.format_prot = self.format_fasta

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

    def format_fasta(self, instream, outstream, logstream=sys.stderr):
        for line in instream:
            if line.startswith('>'):
                pattern = '>gi\|\d+\|(ref|gb)\|([^\|]+)\S+'
                line = re.sub(pattern, '>\g<2>', line)
            print(line, end='', file=outstream)

    def format_gff3(self, logstream=sys.stderr, debug=False):
        cmds = list()
        cmds.append('gunzip -c %s' % self.gff3path)
        excludefile = self.filter_file()
        cmds.append('grep -vf %s' % excludefile.name)
        cmds.append('genhub-fix-trna.py')
        cmds.append('tidygff3')
        cmds.append('genhub-format-gff3.py --source ncbi_flybase -')
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
        os.unlink(excludefile.name)

    def gff3_protids(self, instream):
        protids = dict()
        for line in instream:
            if '\tCDS\t' not in line:
                continue
            idmatch = re.search('protein_id=([^;\n]+)', line)
            assert idmatch, 'cannot parse protein_id: ' + line
            protid = idmatch.group(1)
            if protid not in protids:
                protids[protid] = True
                yield protid

    def protein_mapping(self, instream):
        locusid2name = dict()
        gene2loci = dict()
        mrna2gene = dict()
        proteins = dict()
        for line in instream:
            fields = line.split('\t')
            if len(fields) != 9:
                continue
            feattype = fields[2]
            attrs = fields[8]

            if feattype == 'locus':
                idmatch = re.search('ID=([^;\n]+);.*Name=([^;\n]+)', attrs)
                if idmatch:
                    locusid = idmatch.group(1)
                    locusname = idmatch.group(2)
                    locusid2name[locusid] = locusname
            elif feattype == 'gene':
                idmatch = re.search('ID=([^;\n]+);Parent=([^;\n]+)', attrs)
                assert idmatch, \
                    'Unable to parse gene and iLocus IDs: %s' % attrs
                geneid = idmatch.group(1)
                ilocusid = idmatch.group(2)
                gene2loci[geneid] = ilocusid
            elif feattype == 'mRNA':
                idmatch = re.search('ID=([^;\n]+);Parent=([^;\n]+)', attrs)
                assert idmatch, \
                    'Unable to parse mRNA and gene IDs: %s' % attrs
                mrnaid = idmatch.group(1)
                geneid = idmatch.group(2)
                mrna2gene[mrnaid] = geneid
            elif feattype == 'CDS':
                idmatch = re.search('Parent=([^;\n]+).*protein_id=([^;\n]+)',
                                    attrs)
                assert idmatch, \
                    'Unable to parse protein and mRNA IDs: %s' % attrs
                mrnaid = idmatch.group(1)
                proteinid = idmatch.group(2)
                if proteinid not in proteins:
                    geneid = mrna2gene[mrnaid]
                    proteins[proteinid] = mrnaid
                    ilocusid = gene2loci[geneid]
                    ilocusname = locusid2name[ilocusid]
                    yield proteinid, ilocusname


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_chromosomes():
    """NCBI/FlyBase chromosome download"""
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config)

    testurls = ['ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_X/NC_004354.fna',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_2/NT_033778.fna',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_2/NT_033779.fna',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_3/NT_033777.fna',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_3/NT_037436.fna',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_4/NC_004353.fna']
    testpath = './Dmfb/Dmfb.orig.fa.gz'
    assert dmel_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (dmel_db.gdnaurl, testurls)
    assert dmel_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (dmel_db.gdnapath, testpath)
    assert '%r' % dmel_db == 'FlyBase@NCBI'
    assert dmel_db.compress_gdna is True


def test_annot():
    """NCBI/FlyBase annotation download"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config)

    testurls = ['ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_X/NC_004354.gff',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_2/NT_033778.gff',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_2/NT_033779.gff',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_3/NT_033777.gff',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_3/NT_037436.gff',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_4/NC_004353.gff']
    testpath = './Dmfb/dmel-5.48-ncbi.gff3.gz'
    assert dmel_db.gff3url == testurls, \
        'annotation URL mismatch\n%s\n%s' % (dmel_db.gff3url, testurls)
    assert dmel_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (dmel_db.gff3path, testpath)
    assert dmel_db.compress_gff3 is True


def test_proteins():
    """NCBI/FlyBase protein download"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config)

    testurls = ['ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_X/NC_004354.faa',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_2/NT_033778.faa',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_2/NT_033779.faa',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_3/NT_033777.faa',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_3/NT_037436.faa',
                'ftp://ftp.ncbi.nih.gov/genomes/archive/old_refseq/'
                'Drosophila_melanogaster/RELEASE_5_48/CHR_4/NC_004353.faa']
    testpath = './Dmfb/protein.fa.gz'
    assert dmel_db.proturl == testurls, \
        'protein URL mismatch\n%s\n%s' % (dmel_db.proturl, testurls)
    assert dmel_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (dmel_db.protpath, testpath)
    assert dmel_db.compress_prot is True


def test_format():
    """Task drivers"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config, workdir='testdata/demo-workdir')
    dmel_db.format(logstream=None, verify=False)


def test_gdna_format():
    """NCBI/FlyBase gDNA formatting"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config, workdir='testdata/demo-workdir')

    dmel_db.preprocess_gdna(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Dmfb/Dmfb.gdna.fa'
    testoutfile = 'testdata/fasta/dmel-fb-gdna-ut-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Dmfb gDNA formatting failed'


def test_annot_format():
    """NCBI/FlyBase annotation formatting"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config, workdir='testdata/demo-workdir')

    dmel_db.preprocess_gff3(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Dmfb/Dmfb.gff3'
    testfile = 'testdata/gff3/ncbi-format-dmel.gff3'
    assert filecmp.cmp(outfile, testfile), 'Dmfb annotation formatting failed'


def test_prot_format():
    """NCBI/FlyBase protein formatting"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config, workdir='testdata/demo-workdir')

    dmel_db.preprocess_prot(logstream=None, verify=False)
    outfile = 'testdata/demo-workdir/Dmfb/Dmfb.all.prot.fa'
    testoutfile = 'testdata/fasta/dmel-fb-prot-ut-out.fa'
    assert filecmp.cmp(testoutfile, outfile), 'Dmfb protein formatting failed'


def test_protids():
    """NCBI/FlyBase: extract protein IDs from GFF3"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config)

    protids = ['NP_524820.2', 'NP_001259789.1', 'NP_608489.2']
    infile = 'testdata/gff3/dmel-net.gff3'
    testids = list()
    with open(infile, 'r') as instream:
        for protid in dmel_db.gff3_protids(instream):
            testids.append(protid)
    assert sorted(protids) == sorted(testids), \
        'protein ID mismatch: %r %r' % (protids, testids)


def test_protmap():
    """NCBI/FlyBase: extract protein-->iLocus mapping from GFF3"""
    registry = genhub.registry.Registry()
    config = genhub.test_registry.genome('Dmfb')
    dmel_db = FlyBaseDB('Dmfb', config)

    mapping = {'NP_001259789.1': 'DmfbILC-10965',
               'NP_524820.2': 'DmfbILC-10965',
               'NP_608489.2': 'DmfbILC-10967',
               'NP_608490.1': 'DmfbILC-10968',
               'NP_001259790.1': 'DmfbILC-10968'}
    infile = 'testdata/gff3/dmel-net-loci.gff3'
    testmap = dict()
    with open(infile, 'r') as instream:
        for protid, locid in dmel_db.protein_mapping(instream):
            testmap[protid] = locid
    assert mapping == testmap, \
        'protein mapping mismatch: %r %r' % (mapping, testmap)
