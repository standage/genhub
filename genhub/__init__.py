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
from . import registry
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


# Unit test fixtures (can't figure out how to do package-scope global fixtures
# with nose's setup and teardown mechanism).
test_registry = registry.Registry()
test_registry_supp = registry.Registry()
test_registry_supp.update('testdata/conf')
