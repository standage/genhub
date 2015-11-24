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

This "superclass" defines many default characteristics and behaviors that are
shared across different genome databases. Subclasses implement additional
specifics for managing data from a particular source.
"""

from __future__ import print_function
import gzip
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

    def format(self, logstream=sys.stderr, verify=True):  # pragma: no cover
        """Run format task"""
        self.preprocess_gdna(logstream=logstream, verify=verify)
        self.preprocess_gff3(logstream=logstream, verify=verify)
        self.preprocess_prot(logstream=logstream, verify=verify)

    def preprocess(self, datatype, instream=None, outstream=None,
                   logstream=sys.stderr, verify=True):
        """
        Preprocess genome data files.

        To read from or write to a custom input/output streams (rather than the
        default file locations), set `instream` and/or `outstream` to a
        readable or writeable file handle, a stringio, or similar object.

        Note that this is a wrapper function: each subclass must implement 3
        methods (`format_gdna`, `format_gff3`, and `format_prot`) to do the
        actual formatting.
        """
        messages = {'gdna': 'genome sequence file',
                    'gff3': 'annotation file',
                    'prot': 'protein sequence file'}
        assert datatype in messages

        if logstream is not None:  # pragma: no cover
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'preprocess %s' % messages[datatype]
            print(logmsg, file=logstream)

        outfile = None
        if datatype == 'gdna':
            streamin = instream
            if instream is None:
                if self.gdnapath.endswith('.gz'):
                    streamin = gzip.open(self.gdnapath, 'rt')
                else:
                    streamin = open(self.gdnapath, 'r')
            streamout = outstream
            if outstream is None:
                streamout = open(self.gdnafile, 'w')
                outfile = self.gdnafile
            self.format_gdna(streamin, streamout, logstream)
            if instream is None:
                streamin.close()
            if outstream is None:
                streamout.close()

        elif datatype == 'gff3':
            self.format_gff3(logstream)
            outfile = self.gff3file

        elif datatype == 'prot':
            streamin = instream
            if instream is None:
                if self.protpath.endswith('.gz'):
                    streamin = gzip.open(self.protpath, 'rt')
                else:
                    streamin = open(self.protpath, 'r')
            streamout = outstream
            if outstream is None:
                streamout = open(self.protfile, 'w')
                outfile = self.protfile
            self.format_prot(streamin, streamout, logstream)
            if instream is None:
                streamin.close()
            if outstream is None:
                streamout.close()

        if verify is False:
            return

        if outstream is None or datatype == 'gff3':
            if 'checksums' in self.config and \
               datatype in self.config['checksums']:
                testsha1 = genhub.file_sha1(outfile)
                assert testsha1 == self.config['checksums'][datatype], \
                    '%s %s integrity check failed' % (self.label,
                                                      messages[datatype])
            else:  # pragma: no cover
                message = 'Cannot verify integrity of %s ' % self.label
                message += '%s without a checksum' % messages[datatype]
                print(message, file=logstream)

    def preprocess_gdna(self, instream=None, outstream=None,
                        logstream=sys.stderr, verify=True):
        self.preprocess('gdna', instream, outstream, logstream, verify)

    def preprocess_gff3(self, logstream=sys.stderr, verify=True):
        self.preprocess('gff3', None, None, logstream, verify)

    def preprocess_prot(self, instream=None, outstream=None,
                        logstream=sys.stderr, verify=True):
        self.preprocess('prot', instream, outstream, logstream, verify)


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
