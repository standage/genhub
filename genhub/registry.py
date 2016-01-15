#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015-2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015-2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Module implementing a registry for handling genome configuration files."""

from __future__ import print_function
import glob
import os
import pkg_resources
import yaml
import genhub
try:
    FileNotFoundError
except NameError:  # pragma: no cover
    FileNotFoundError = IOError


class Registry(object):

    def __init__(self):
        """Initialize the registry with the default GenHub configs."""
        genhubdir = pkg_resources.resource_filename('genhub', 'genomes')
        self.update(genhubdir, clear=True)

    def update(self, path, clear=False):
        """
        Update the registry from the given directory path.

        The registry will attempt to load all .yml files as genome configs and
        .txt files as batch configs. If `clear` is true, any previous entries
        in the registry will be cleared before loading new entries.
        """
        if clear:
            self.genome_configs = dict()
            self.batch_configs = dict()

        if not os.path.exists(path):
            message = 'config directory "%s" does not exist' % path
            raise FileNotFoundError(message)

        for filepath in glob.glob(path + '/*.yml'):
            configs = self.parse_genome_config(filepath)
            self.genome_configs.update(configs)

        for filepath in glob.glob(path + '/*.txt'):
            batch = self.parse_batch_config(filepath)
            filename = os.path.basename(filepath)
            batch_label = os.path.splitext(filename)[0]
            self.batch_configs[batch_label] = batch

    def genome(self, label):
        """Retrieve a genome config from the registry by label."""
        if label not in self.genome_configs:
            return None
        return self.genome_configs[label]

    def genomes(self, labels):
        config = dict()
        for label in labels:
            config[label] = self.genome_configs[label]
        return config

    def batch(self, batch_label):
        """Retrieve a batch of genome configs from the registry."""
        if batch_label not in self.batch_configs:
            return None
        config = dict()
        for genome_label in self.batch_configs[batch_label]:
            config[genome_label] = self.genome_configs[genome_label]
        return config

    def parse_genome_config(self, config):
        """
        Parse genome config in YAML format.

        If `config` is a string it is treated as a filename, otherwise as a
        file handle or similar object.
        """
        if isinstance(config, str):
            config = open(config, 'r')
        return yaml.load(config)

    def parse_batch_config(self, config):
        """
        Parse a batch of genome config labels from a file.

        The file should contain a single genome config label per line, and
        `config` is treated as a filename.
        """
        batch = list()
        with open(config, 'r') as infile:
            for line in infile:
                label = line.strip()
                if label != '':
                    batch.append(label)
        return batch

    def list_genomes(self):
        for label in sorted(self.genome_configs):
            yield label, self.genome_configs[label]

    def list_batches(self):
        for label in sorted(self.batch_configs):
            yield label, self.batch_configs[label]


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_list():
    """Listing genome and batch configs"""
    registry = Registry()

    genome_labels = [x for x in registry.list_genomes()]
    ymlfiles = [x for x in glob.glob('genhub/genomes/*.yml')]
    assert len(genome_labels) == len(ymlfiles)
    batch_labels = [x for x in registry.list_batches()]
    txtfiles = [x for x in glob.glob('genhub/genomes/*.txt')]
    assert len(batch_labels) == len(txtfiles)

    registry.update('testdata/conf', clear=True)

    genome_labels = [x for x in registry.list_genomes()]
    ymlfiles = [x for x in glob.glob('testdata/conf/*.yml')]
    assert len(genome_labels) == len(ymlfiles)
    batch_labels = [x for x in registry.list_batches()]
    txtfiles = [x for x in glob.glob('testdata/conf/*.txt')]
    assert len(batch_labels) == len(txtfiles)

    try:
        registry.update('foobar/bogus')
    except FileNotFoundError:
        pass


def test_genome():
    """Loading a genome configuration by label"""
    registry = Registry()
    config = registry.genome('Osat')
    assert 'accession' in config
    assert config['accession'] == 'GCF_000005425.2'

    registry.update('testdata/conf')
    config = registry.genome('Osat')
    assert 'accession' in config
    assert config['accession'] == 'BogusThisIsNotARealAccession'

    config = registry.genome('Bvul')
    assert 'scaffolds' in config
    assert config['scaffolds'] == 'bv_ref_1.1_chrUn.fa.gz'

    config = registry.genomes(['Atha', 'Bdis', 'Osat'])
    assert len(config) == 3
    assert sorted(config) == ['Atha', 'Bdis', 'Osat']

    assert registry.genome('Docc') is None


def test_batch():
    """Loading a batch configuration by label"""
    registry = Registry()
    config = registry.batch('honeybees')
    assert len(config) == 3
    assert sorted(config) == ['Ador', 'Aflo', 'Amel']

    registry.update('testdata/conf')
    config = registry.batch('mythical')
    assert len(config) == 1
    assert sorted(config) == ['Bvul']

    assert registry.batch('nonexistent') is None

    config = registry.batch('bumblebees')
    assert len(config) == 2
    assert sorted(config) == ['Bimp', 'Bter']
    assert config['Bter']['accession'] == 'GCF_000214255.1'
    assert config['Bimp']['accession'] == 'BogusAccessionForUnitTesting'


def test_parse_genome_config():
    """Parsing genome configurations from a file"""
    registry = Registry()
    with open('genhub/genomes/Pbar.yml', 'r') as filehandle:
        config = registry.parse_genome_config(filehandle)
        assert len(config) == 1
        assert 'Pbar' in config
        assert config['Pbar']['species'] == 'Pogonomyrmex barbatus'

    config = registry.parse_genome_config('genhub/genomes/Hlab.yml')
    assert len(config) == 1
    assert 'Hlab' in config
    assert config['Hlab']['common'] == 'blueberry bee'
