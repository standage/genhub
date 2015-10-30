#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Module for handling configuration files."""

from __future__ import print_function
import glob
import itertools
import yaml
import genhub


def load_file(cfgfile):
    """Load a genome configuration file."""
    if isinstance(cfgfile, str):
        cfgfile = open(cfgfile, 'r')
    return yaml.load(cfgfile)


def load_one(filename):
    """Load a genome configuration file containing a single genome."""
    conf = load_file(filename)
    label = list(conf.keys())[0]
    return label, conf[label]


def load_dir(dirname):
    """
    Load a directory of configuration files.

    All files in the given directory with the suffix `.yml` will be loaded and
    inspected.
    """
    configs = dict()
    filelist = glob.glob(dirname + '/*.yml')
    for filename in filelist:
        conf = load_file(filename)
        configs.update(conf)
    return configs


def load_file_list(cfglist):
    """
    Load a list of configuration files.

    A file list is expected to be a YAML file with a single genome
    configuration file per line, preceded by `- ` (indicating a list/array
    structure).
    """
    if isinstance(cfglist, str):
        cfglist = open(cfglist, 'r')
    config = dict()
    for filename in yaml.load(cfglist):
        with open(filename, 'r') as filehandle:
            config.update(yaml.load(filehandle))
    return config


def test_load_file():
    """Loading genome configurations from a single file"""
    fh = open('conf/test/Emon.yml', 'r')
    conf = load_file(fh)
    assert len(conf) == 1
    assert 'Emon' in conf
    assert conf['Emon']['species'] == 'Equus monoceros'

    conf = load_file('conf/test/Docc.yml')
    assert len(conf) == 1
    assert 'Docc' in conf
    assert conf['Docc']['common'] == 'red dragon'

    label, conf = load_one('conf/test/Bvul.yml')
    assert label == 'Bvul'
    assert conf['source'] == 'ncbi'


def test_load_dir():
    """Loading genome configurations from a directory"""
    conf = load_dir('conf/test')
    assert len(conf) == 4
    assert sorted(conf) == ['Bvul', 'Docc', 'Emon', 'Epeg']

    conf = load_dir('conf/HymHub')
    assert len(conf) == 18
    assert sorted(conf)[0:4] == ['Acep', 'Ador', 'Aech', 'Aflo']


def test_load_list():
    """Loading genome configurations from a file list"""
    conf = load_file_list('conf/honeybees.yml')
    assert len(conf) == 3
    assert sorted(conf) == ['Ador', 'Aflo', 'Amel']

    conf = load_file_list(open('conf/bumblebees.yml', 'r'))
    assert len(conf) == 2
    assert sorted(conf) == ['Bimp', 'Bter']
