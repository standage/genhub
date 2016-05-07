#!/usr/bin/env python
# coding: utf-8
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015-2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015-2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Package-wide configuration"""

# Package modules
from __future__ import print_function
from . import registry
from . import download
from . import fasta
from . import cdhit
from . import genomedb
from . import refseq
from . import beebase
from . import crg
from . import tair
from . import generic
from . import iloci
from . import proteins
from . import mrnas
from . import exons
from . import stats
try:
    FileNotFoundError
except NameError:  # pragma: no cover
    FileNotFoundError = IOError

# Custom modules
from . import am10
from . import pdom

# Versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


# Unit test fixtures (can't figure out how to do package-scope global fixtures
# with nose's setup and teardown mechanism).
test_registry = registry.Registry()
test_registry_supp = registry.Registry()
try:
    # This will only work when the current working directory is the GenHub
    # root directory. Fine since it's only for development.
    test_registry_supp.update('testdata/conf')
except FileNotFoundError:  # pragma: no cover
    pass


sources = {
    'refseq': 'NCBI RefSeq',
    'beebase': 'BeeBase Consortium',
    'crg': 'Wasp/ant genome project (Centro de Regulación Genómica)',
    'pdom': 'Paper wasp genome project (Toth Lab)',
    'tair': 'TAIR6 (The Arabidopsis Information Resource)',
    'am10': 'Amel OGSv1.0 (Honeybee Genome Sequencing Consortium)',
    'local': 'user-supplied genome (local file system)'
}

dbtype = {
    'refseq': refseq.RefSeqDB,
    'beebase': beebase.BeeBaseDB,
    'crg': crg.CrgDB,
    'pdom': pdom.PdomDB,
    'tair': tair.TairDB,
    'am10': am10.Am10DB,
    'local': generic.GenericDB,
}
