GenHub
======

![Supported Python versions](https://img.shields.io/pypi/pyversions/genhub.svg)
[![PyPI version][pypiv]](https://pypi.python.org/pypi/genhub)
[![GenHub build status][travisbadge]](https://travis-ci.org/standage/genhub)
[![BSD-3 licensed][bsd]](https://github.com/standage/genhub/blob/master/LICENSE.txt)

## Summary

GenHub is software for managing a hub of annotated genome assemblies.
It comes configured with simple recipes to collect and standardize genome data from a variety of sources, and it is easy to extend with recipes for additional data.
The interval locus (iLocus) is the primary unit of organization: see the documentation for the [AEGeAn Toolkit][agn_rtd] for more information.

GenHub is primarily designed as a data distribution and reproducibility mechanism.
Because each processed data set includes many non-standard files and occupies >1 gigabyte of storage space (>10G for mammals), finding stable public long-term storage is problematic.
So rather than distributing the processed data itself, GenHub distributes stable code that enables the user to retrieve, process, and store the data using their own computing resources.

## Obtaining GenHub

The easiest way to obtain GenHub is to install from the Python Package Index (PyPI) using the `pip` command.

```bash
pip install genhub
```

You can also install directly from the source.
Check for the latest stable version on the [release listing][rel].

```bash
# replace x.y.z with an actual version
wget https://github.com/standage/genhub/archive/x.y.z.tar.gz
tar -xzf x.y.z.tar.gz
cd genhub-x.y.z
python setup.py install
```

GenHub relies on additional third-party software.
For more info and troubleshooting tips, be sure to check out the complete [installation instructions](docs/INSTALL.md).

## Quick start

```bash
# Download and prepare the yeast genome
genhub-build.py --workdir=/opt/data/myhub --cfg=$GENHUBDIR/conf/modorg/Scer.yml download format prepare stats

# Download and prepare 23 Hymenopteran genomes, 4 at a time
find $GENHUBDIR/conf/hym -type f -name "*.yml" \
    | parallel --gnu --jobs 4 genhub-build.py --workdir=/opt/data/myhub --cfg={} download format prepare stats
```

## Additional Details

GenHub was originally dubbed *HymHub* and was designed specifically for managing hymenotperan genomes.
The need for a more general solution motivated the development of GenHub in its current incarnation.

- Built by Daniel Standage <daniel.standage@gmail.com>
- Development repository at https://github.com/standage/genhub

[travisbadge]: https://img.shields.io/travis/standage/genhub.svg
[pypiv]: https://img.shields.io/pypi/v/genhub.svg
[bsd]: https://img.shields.io/pypi/l/genhub.svg
[agn_rtd]: http://aegean.readthedocs.org
[rel]: https://github.com/standage/genhub/releases
