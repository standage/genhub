GenHub
======

![Supported Python versions](https://img.shields.io/pypi/pyversions/genhub.svg)
[![PyPI version][pypiv]](https://pypi.python.org/pypi/genhub)
[![GenHub build status][travisbadge]](https://travis-ci.org/standage/genhub)
[![BSD-3 licensed][bsd]](https://github.com/standage/genhub/blob/master/LICENSE.txt)

## Summary

GenHub is software for managing a hub of annotated genome assemblies.
It comes configured to retrieve and format dozens of genomes from a variety of sources, and it is easy to extend with configurations for additional genomes.

The interval locus (*iLocus*) is the primary unit of organization in GenHub.
Each iLocus captures the genomic context of a single gene, a group of overlapping genes, or an intergenic region.
iLoci provide a detailed and granular representation of the entire genome that is robust to improvements to the assembly and annotation.
See the documentation for the [AEGeAn Toolkit][agn_rtd] for more information.

GenHub was originally designed as a data distribution and reproducibility mechanism.
Because each processed genome data set includes many non-standard files and occupies >1 gigabyte of storage space (>10G for mammals), stable public long-term storage is not easy to come by.
So rather than distributing the processed data itself, GenHub distributes stable code that enables the user to retrieve, process, and store the data using their own computing resources.
This is all tied closely to our research philosophy and our conviction that published computational results (along with supporting software and data) should be reproducible and transparent.

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
# List all available genomes
genhub-build.py list

# Download and process the yeast genome
genhub-build.py --workdir=/opt/data/myhub --genome=Scer download format prepare stats

# Download and process 23 Hymenopteran genomes, 4 at a time
genhub-build.py --workdir=/opt/data/myhub --batch=hymenoptera --numprocs=4 download format prepare stats
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
