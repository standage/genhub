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
Class for managing a genome database.

By "genome database" we mean a collection of sequence, annotation, and
ancillary data files for a annotated genome assembly.
"""

from __future__ import print_function
import subprocess
import sys
import genhub


class GenomeDB():

    def __init__(self, label, conf, workdir='.'):
        self.label = label
        self.config = conf
        self.workdir = workdir
        assert 'source' in conf, 'data source unconfigured'

    # ----------
    # Filenames for unprocessed data from the primary source.
    # ----------

    @property
    def gdnafilename(self):
        if 'scaffolds' in self.config:
            return self.config['scaffolds']
        elif 'chromosomes' in self.config:
            return '%s.orig.fa.gz' % self.label
        return None  # pragma: no cover

    @property
    def gff3filename(self):
        return self.config['annotation']

    @property
    def protfilename(self):
        if 'proteins' in self.config:
            return self.config['proteins']
        return 'protein.fa.gz'

    # ----------
    # Complete file paths for unprocessed data.
    # ----------

    @property
    def gdnapath(self):
        return genhub.file_path(self.gdnafilename, self.label, self.workdir)

    @property
    def gff3path(self):
        return genhub.file_path(self.gff3filename, self.label, self.workdir)

    @property
    def protpath(self):
        return genhub.file_path(self.protfilename, self.label, self.workdir)

    # ----------
    # File paths for processed data.
    # ----------

    @property
    def gdnafile(self):
        filename = '%s.gdna.fa' % self.label
        return genhub.file_path(filename, self.label, self.workdir)

    @property
    def gff3file(self):
        filename = '%s.gff3' % self.label
        return genhub.file_path(filename, self.label, self.workdir)

    @property
    def protfile(self):
        filename = '%s.all.prot.fa' % self.label
        return genhub.file_path(filename, self.label, self.workdir)

    # ----------
    # Determine whether raw data files need to be compressed during download.
    # ----------

    @property
    def compress_gdna(self):
        if 'compress' in self.config and 'gdna' in self.config['compress']:
            return True
        return False

    @property
    def compress_gff3(self):
        if 'compress' in self.config and 'gff3' in self.config['compress']:
            return True
        return False

    @property
    def compress_prot(self):
        if 'compress' in self.config and 'prot' in self.config['compress']:
            return True
        return False

    # ----------
    # Miscellaneous properties.
    # ----------

    @property
    def source(self):
        """The institutional source of the data."""
        return self.config['source']

    @property
    def dbdir(self):
        """Dedicated directory for this genome database."""
        return '%s/%s' % (self.workdir, self.label)

    # ----------
    # Build task method implementations.
    # ----------

    def download_gdna(self, logstream=sys.stderr):  # pragma: no cover
        """Download genomic DNA sequence."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download genome sequence from %r' % self
            print(logmsg, file=logstream)
        genhub.download.url_download(self.gdnaurl, self.gdnapath,
                                     compress=self.compress_gdna)

    def download_gff3(self, logstream=sys.stderr):  # pragma: no cover
        """Download genome annotation."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download genome annotation from %r' % self
            print(logmsg, file=logstream)
        genhub.download.url_download(self.gff3url, self.gff3path,
                                     compress=self.compress_gff3)

    def download_prot(self, logstream=sys.stderr):  # pragma: no cover
        """Download protein sequences."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download protein sequences from %r' % self
            print(logmsg, file=logstream)
        genhub.download.url_download(self.proturl, self.protpath,
                                     compress=self.compress_prot)

    def download(self, logstream=sys.stderr):  # pragma: no cover
        """Run download task."""
        self.download_gdna(logstream)
        self.download_gff3(logstream)
        self.download_prot(logstream)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_props():
    """GenomeDB properties"""
    label, config = genhub.conf.load_one('conf/HymHub/Bimp.yml')
    db = GenomeDB(label, config)
    assert db.dbdir == './Bimp'
    assert db.gdnafile == './Bimp/Bimp.gdna.fa'
    assert db.gff3file == './Bimp/Bimp.gff3'
    assert db.protfile == './Bimp/Bimp.all.prot.fa'
    assert db.source == 'ncbi'

    label, config = genhub.conf.load_one('conf/HymHub/Dqua.yml')
    db = GenomeDB(label, config, workdir='/opt/data/genomes')
    assert db.dbdir == '/opt/data/genomes/Dqua'
    assert db.gdnafile == '/opt/data/genomes/Dqua/Dqua.gdna.fa'
    assert db.gff3file == '/opt/data/genomes/Dqua/Dqua.gff3'
    assert db.protfile == '/opt/data/genomes/Dqua/Dqua.all.prot.fa'
    assert db.source == 'crg'
