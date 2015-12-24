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
import tempfile
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


def test_load_file():
    """Loading genome configurations from a single file"""
    fh = open('conf/hym/Pbar.yml', 'r')
    conf = load_file(fh)
    assert len(conf) == 1
    assert 'Pbar' in conf
    assert conf['Pbar']['species'] == 'Pogonomyrmex barbatus'

    conf = load_file('conf/hym/Hlab.yml')
    assert len(conf) == 1
    assert 'Hlab' in conf
    assert conf['Hlab']['common'] == 'blueberry bee'

    label, conf = load_one('conf/modorg/Tcas.yml')
    assert label == 'Tcas'
    assert conf['source'] == 'refseq'


def test_load_dir():
    """Loading genome configurations from a directory"""
    conf = load_dir('conf/hym')
    assert len(conf) == 23
    assert sorted(conf)[0:4] == ['Acep', 'Ador', 'Aech', 'Aflo']


def test_load_list():
    """Loading genome configurations from a file list"""
    conf = load_file_list('conf/honeybees.yml')
    assert len(conf) == 3
    assert sorted(conf) == ['Ador', 'Aflo', 'Amel']

    conf = load_file_list(open('conf/bumblebees.yml', 'r'))
    assert len(conf) == 2
    assert sorted(conf) == ['Bimp', 'Bter']
