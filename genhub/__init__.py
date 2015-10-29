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
import os
from . import conf
from . import download
from . import ncbi
from . import format

# Custom modules
from . import pdom

# Versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def file_path(filename, speclabel, workdir='.', check=False, message=None):
    """
    Resolve a file's complete path, optionally checking if the file exists.
    """
    filepath = '%s/%s/%s' % (workdir, speclabel, filename)
    if check:
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
