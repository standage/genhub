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
import yaml
import genhub


def load_file(cfgfile):
    if isinstance(cfgfile, str):
        cfgfile = open(cfgfile, 'r')
    return yaml.load(cfgfile)


def load_one(filename):
    conf = load_file(filename)
    label = list(conf.keys())[0]
    return label, conf[label]


def load_dir(dirname):
    configs = dict()
    filelist = glob.glob(dirname + '/*.yml')
    for filename in filelist:
        conf = load_file(filename)
        for label in conf:
            configs[label] = conf
    return configs


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
