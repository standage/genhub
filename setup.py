#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Setup configuration for genhub"""

import setuptools
import versioneer


setuptools.setup(name='genhub',
                 version=versioneer.get_version(),
                 cmdclass=versioneer.get_cmdclass(),
                 description=('Collect and pre-process annotated genome '
                              'assemblies'),
                 url='http://github.com/standage/genhub',
                 author='Daniel Standage',
                 author_email='daniel.standage@gmail.com',
                 license='BSD-3',
                 packages=['genhub'],
                 scripts=['scripts/genhub-build.py',
                          'scripts/genhub-filens.py',
                          'scripts/genhub-fix-trna.py',
                          'scripts/genhub-format-gff3.py',
                          'scripts/genhub-namedup.py',
                          'scripts/genhub-stats.py'],
                 package_data={'genhub': ['../conf/*.yml',
                                          '../conf/*/*.yml']},
                 zip_safe=False)
