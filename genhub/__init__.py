#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Package-wide configuration"""

# Package modules
from __future__ import print_function
import hashlib
import os
import sys
from . import conf
from . import download
from . import fasta
from . import genomedb
from . import refseq
from . import ncbi_flybase
from . import beebase
from . import crg
from . import iloci
from . import proteins
from . import mrnas
from . import exons
from . import stats

# Custom modules
from . import pdom

# Versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


ghdir = os.path.dirname(os.path.realpath(__file__))
scriptdir = os.path.realpath(ghdir + '/../scripts/')
os.environ['PATH'] += ':' + scriptdir


def file_path(filename, speclabel, workdir='.', check=False, message=None):
    """
    Resolve a file's complete path, optionally checking if the file exists.
    """
    filepath = '%s/%s/%s' % (workdir, speclabel, filename)
    if check:  # pragma: no cover
        msg = 'file "%s" not found' % filepath
        if message is not None:
            msg += '; %s' % message
        assert os.path.exists(filepath), msg
    return filepath


def test_file_path():
    """File name resolution"""
    assert file_path('bogus.txt', 'Emon', workdir='.') == './Emon/bogus.txt'
    assert file_path('Docc.gff3', 'Docc', 'wd') == 'wd/Docc/Docc.gff3'
    checkfailed = False
    try:
        path = file_path('Amel.iloci.gff3', 'Amel', check=True)
    except AssertionError as e:
        checkfailed = True
        assert e.args[0] == 'file "./Amel/Amel.iloci.gff3" not found'
    assert checkfailed


def file_sha1(filepath):
    """Stolen shamelessly from http://stackoverflow.com/a/19711609/459780."""
    sha = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(2**10)
            if not block:
                break
            sha.update(block)
        return sha.hexdigest()
