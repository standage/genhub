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
import shutil
import subprocess


def check_import(genhubroot='.', dev=False):
    """Check for Python modules."""
    print('[GenHub] Checking Python modules.')

    devmod = ['pep8', 'nose', 'coverage']
    reqfilename = '%s/requirements.txt' % genhubroot
    reqfile = open(reqfilename, 'r')
    packages = dict()
    for line in reqfile:
        pkg = line.rstrip()
        if pkg in devmod and dev is False:
            continue
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
        print('Run "make depend" to install missing packages.', end='')
        print(' See "README.md".')


def check_path():
    """
    Check PATH for executables and scripts.

    Using shutils.which would be much cleaner, but it is unfortunately not
    backported to Python 2.7.x.
    """
    print('[GenHub] Checking PATH for executables and scripts.')

    execs = ['gt', 'tidygff3', 'locuspocus', 'xtractore', 'canon-gff3',
             'lpdriver.py', 'uloci.py', 'seq-reg.py']
    paths = list()
    for exe in execs:
        try:
            proc = subprocess.Popen(['which', exe], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
            resultcode = proc.wait()
            if resultcode == 0:
                procpath = next(proc.stdout)
                procpath = str(procpath).rstrip()
                paths.append((exe, procpath))
            else:
                paths.append((exe, None))
        except subprocess.CalledProcessError:
            paths.append((exe, None))

    missing = False
    for exe, path in paths:
        char = '+'
        if path is None:
            char = '-'
            path = '???'
            missing = True
        print('%s %-20s: %s' % (char, exe, path))
    if missing:
        print('Executables / scripts cannot be found in your PATH.', end='')
        print(' Certain build commands will not work.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dev', action='store_true',
                        help='Check for developer-only modules as well')
    parser.add_argument('-r', '--root', default='.',
                        help='GenHub root directory')
    args = parser.parse_args()

    check_import(genhubroot=args.root, dev=args.dev)
    check_path()
