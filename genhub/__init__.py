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
