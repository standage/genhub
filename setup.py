#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015-2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015-2016   Indiana University
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
                 description=('Explore eukaryotic genome composition and '
                              'organization with iLoci'),
                 url='http://github.com/standage/genhub',
                 author='Daniel Standage',
                 author_email='daniel.standage@gmail.com',
                 license='BSD-3',
                 packages=['genhub'],
                 scripts=['scripts/fidibus',
                          'scripts/genhub-filens.py',
                          'scripts/genhub-fix-trna.py',
                          'scripts/genhub-format-gff3.py',
                          'scripts/genhub-glean-to-gff3.py',
                          'scripts/genhub-namedup.py',
                          'scripts/genhub-ilocus-summary.py',
                          'scripts/genhub-pilocus-summary.py',
                          'scripts/genhub-milocus-summary.py',
                          'scripts/genhub-stats.py',
                          'scripts/genhub-compact.py'],
                 install_requires=['pyyaml', 'pycurl'],
                 package_data={'genhub': ['genomes/*.yml', 'genomes/*.txt']},
                 classifiers=[
                    'Development Status :: 4 - Beta',
                    'Environment :: Console',
                    'License :: OSI Approved :: BSD License',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 3.3',
                    'Programming Language :: Python :: 3.4',
                    'Programming Language :: Python :: 3.5',
                    'Topic :: Scientific/Engineering :: Bio-Informatics'
                 ],
                 zip_safe=False)
