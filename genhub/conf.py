#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Module for handling genome configuration files."""

from __future__ import print_function
import itertools
import os
import pkg_resources
import tempfile
import yaml
import genhub
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def load_genome(label, user_dirs=None):
    """
    Load a genome configuration file.

    - `label`: the filename of the genome configuration file, without `.yml`
      extension
    - `user_dir`: a list of user-specified directories in which to look for
      configuration files; if specified, they take precedence over the primary
      GenHub genome configuration directory
    """
    cfgdirs = list()
    if user_dirs:
        cfgdirs.extend(user_dirs)
    genhubdir = pkg_resources.resource_filename('genhub', 'genomes')
    cfgdirs.append(genhubdir)

    for cfgdir in cfgdirs:
        cfgfile = '%s/%s.yml' % (cfgdir, label)
        if os.path.isfile(cfgfile):
            with open(cfgfile, 'r') as infile:
                return yaml.load(infile)

    message = 'genome configuration file "%s.yml" not found' % label
    raise FileNotFoundError(message)


def load_genomes(labels, user_dirs=None):
    """Load a list of genome configuration files from memory."""
    config = dict()
    for label in labels:
        cfg = load_genome(label, user_dirs)
        config.update(cfg)
    return config


def load_genomes_from_file(filename, user_dirs=None):
    """
    Load a list of genome configuration files from a file.

    The file should contain a single label per line.
    """
    if not os.path.isfile(filename):
        message = 'unable to locate genome config list file "%s"' % filename
        raise FileNotFoundError(message)

    labels = list()
    with open(filename, 'r') as infile:
        for line in infile:
            label = line.strip()
            if label != '':
                labels.append(label)
    return load_genomes(labels, user_dirs)


def load_genome_list(listlabel, user_dirs=None):
    """
    Load a genome configuration list file.

    Not to be confused with a list of genome configuration files!
    """
    cfgdirs = list()
    if user_dirs:
        cfgdirs.extend(user_dirs)
    genhubdir = pkg_resources.resource_filename('genhub', 'genomes')
    cfgdirs.append(genhubdir)

    for cfgdir in cfgdirs:
        listfile = '%s/%s.txt' % (cfgdir, listlabel)
        if os.path.isfile(listfile):
            return load_genomes_from_file(listfile, user_dirs)

    message = 'genome configuration list file "%s.txt" not found' % listlabel
    raise FileNotFoundError(message)


def load_file(cfgfile):
    """
    Load a genome configuration file.

    Convenience function for development and unit testing.
    """
    if isinstance(cfgfile, str):
        cfgfile = open(cfgfile, 'r')
    return yaml.load(cfgfile)


def load_one(filename):
    """
    Load a genome configuration file containing a single genome.

    Convenience function for development and unit testing. The user will not
    typically provide full filenames for config files, and the current script
    CLI does not make this convenient either.
    """
    conf = load_file(filename)
    label = list(conf.keys())[0]
    return label, conf[label]


def conf_filter_file(conf):
    """
    Write exclusion filter to a temporary file and return.

    Data configurations may include an optional `annotfilter` with patterns to
    discard from the input annotation a la `grep -v`. This function reads the
    pattern(s) from the data configuration and writes them to a temporary file
    that can be used in a `grep -vf` command. Calling function is responsible
    for unlinking the temporary file from the operating system.
    """
    assert 'annotfilter' in conf
    excludefile = tempfile.NamedTemporaryFile(mode='wt', delete=False)
    if isinstance(conf['annotfilter'], str):
        print(conf['annotfilter'], file=excludefile)
    else:
        for exclusion in conf['annotfilter']:
            print(exclusion, file=excludefile)
    excludefile.close()
    return excludefile


def test_load_genome():
    """Load a genome configuration by label"""
    conf = load_genome('Osat')
    print(conf)
    assert len(conf) == 1
    assert 'Osat' in conf
    assert conf['Osat']['accession'] == 'GCF_000005425.2'

    conf = load_genome('Osat', user_dirs=['testdata/conf'])
    assert len(conf) == 1
    assert 'Osat' in conf
    assert conf['Osat']['accession'] == 'BogusThisIsNotARealAccession'

    conf = load_genome('Bvul', user_dirs=['testdata/conf'])
    assert len(conf) == 1
    assert 'Bvul' in conf
    assert conf['Bvul']['scaffolds'] == 'bv_ref_1.1_chrUn.fa.gz'

    try:
        conf = load_genome('Bvul')
    except FileNotFoundError:
        pass


def test_load_genomes():
    """Loading a list of genome configurations"""
    conf = load_genomes(['Ador', 'Aflo', 'Amel'])
    assert len(conf) == 3
    assert sorted(conf) == ['Ador', 'Aflo', 'Amel']

    conf = load_genomes(['Bimp', 'Bter'], user_dirs=['testdata/conf'])
    assert len(conf) == 2
    assert sorted(conf) == ['Bimp', 'Bter']
    assert conf['Bter']['accession'] == 'GCF_000214255.1'
    assert conf['Bimp']['accession'] == 'BogusAccessionForUnitTesting'


def test_load_genome_list():
    """Loading a genome configuration list"""
    conf = load_genome_list('honeybees')
    assert len(conf) == 3
    assert sorted(conf) == ['Ador', 'Aflo', 'Amel']

    conf = load_genome_list('mythical', user_dirs=['testdata/conf'])
    assert len(conf) == 1
    assert sorted(conf) == ['Bvul']

    try:
        conf = load_genome_list('nonexistent')
    except FileNotFoundError:
        pass

    conf = load_genomes_from_file('testdata/conf/bumblebees.txt',
                                  user_dirs=['testdata/conf'])
    assert len(conf) == 2
    assert sorted(conf) == ['Bimp', 'Bter']
    assert conf['Bter']['accession'] == 'GCF_000214255.1'
    assert conf['Bimp']['accession'] == 'BogusAccessionForUnitTesting'

    try:
        conf = load_genomes_from_file('testdata/conf/muggles.txt')
    except FileNotFoundError:
        pass


def test_load_file():
    """Loading genome configurations from a single file"""
    fh = open('genhub/genomes/Pbar.yml', 'r')
    conf = load_file(fh)
    assert len(conf) == 1
    assert 'Pbar' in conf
    assert conf['Pbar']['species'] == 'Pogonomyrmex barbatus'

    conf = load_file('genhub/genomes/Hlab.yml')
    assert len(conf) == 1
    assert 'Hlab' in conf
    assert conf['Hlab']['common'] == 'blueberry bee'

    label, conf = load_one('genhub/genomes/Tcas.yml')
    assert label == 'Tcas'
    assert conf['source'] == 'refseq'
