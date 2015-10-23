#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

from __future__ import print_function
import importlib

reqfile = open('requirements.txt', 'r')
packages = dict()
for line in reqfile:
    pkg = line.rstrip()
    try:
        importlib.import_module(pkg)
        packages[pkg] = True
    except ImportError:
        packages[pkg] = False
try:
    importlib.import_module('yaml')
    packages['pyyaml'] = True
except ImportError:
    packages['pyyaml'] = False

rundep = False
for pkg in packages:
    char = '+'
    msg = 'Installed.'
    if packages[pkg] is False:
        char = '-'
        msg = 'Not installed!'
        rundep = True
    print('%c package %-12s: %s' % (char, pkg, msg))
if rundep is True:
    print('Run "make depend" to install missing packages. See "README.md".')
