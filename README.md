GenHub (deprecated)
===================

**NOTE**: GenHub has been integrated into the [AEGeAn Toolkit](https://github.com/BrendelGroup/AEGeAn) as the [fidibus module](https://github.com/BrendelGroup/AEGeAn/tree/master/fidibus) and **IS NO LONGER ACTIVELY DEVELOPED HERE!!!**

----------

![Supported Python versions](https://img.shields.io/pypi/pyversions/genhub.svg)
[![PyPI version][pypiv]](https://pypi.python.org/pypi/genhub)
[![GenHub build status][travisbadge]](https://travis-ci.org/standage/genhub)
[![codecov.io coverage][codecovbadge]](https://codecov.io/github/standage/genhub)
[![BSD-3 licensed][bsd]](https://github.com/standage/genhub/blob/master/LICENSE.txt)

GenHub is a free [open-source](LICENSE.txt) software framework for analyzing eukaryotic genome content and organization.
The `Fidibus` program calculates and reports a variety of statistics on *interval loci* (*iLoci*).
`Fidibus` can analyze user-supplied genomes, and can also retrieve and process dozens of reference genomes directly from public databases (such as NCBI RefSeq) for easily reproducible comparative analysis.

For or information, see the [GenHub user manual](docs/MANUAL.md)

## Obtaining GenHub

The easiest way to obtain GenHub is to install from the Python Package Index (PyPI) using the `pip` command.

```bash
pip install genhub
```

Make sure you have [GenomeTools](http://genometools.org) and [AEGeAn](http://brendelgroup.github.io/AEGeAn) installed.
For more info and troubleshooting tips, be sure to check out the complete [installation instructions](docs/INSTALL.md).

## Quick start: example usages

```bash
# Show all configuration settings
fidibus --help

# Compute iLoci for a user-supplied genome
fidibus --workdir=./ --local --gdna=MyGenome.fasta --gff3=MyAnnotation.gff3 \
        --prot=MyProteins.fasta --label=Gnm1 \
        prep iloci

# List all available reference genomes
fidibus list

# Download and pre-process the budding yeast genome, but do not compute iLoci
fidibus --workdir=/opt/data/genomes/ --refr=Scer download prep

# Download and completely process a few dozen Hymenopteran genomes, 4 at a time
fidibus --workdir=/opt/data/genomes/ --refr=hymenoptera --numprocs=4 \
        download prep iloci breakdown stats

# Download 9 green algae genomes, cluster proteins to identify homologous iLoci
fidibus --workdir=~/mydata/ --refrbatch=chlorophyta --numprocs=6 \
        download prep iloci breakdown cleanup cluster

# Process a user-supplied genome and several reference genomes for comparison
fidibus --workdir=/data/ --numprocs=4 --local --gdna=MyGenome.fasta \
        --gff3=MyAnnotation.gff3 --prot=MyProteins.fasta --label=Gnm1 \
        --refr=Atha,Bdis,Bole,Cari,Gmax,Grai,Mtru,Osat,Tcac \
        download prep iloci breakdown stats
```

For more detailed instructions on running `Fidibus` and other ancillary scripts, see the [user manual](docs/MANUAL.md).

## Citing GenHub

GenHub is research software and must be cited if it is used in a published research project.
GenHub will soon be in print, but in the mean time it can be cited as follows.

> **Standage DS, Brendel VP** (2016) GenHub. *GitHub repository*, https://github.com/standage/genhub.

## Additional Details

GenHub was originally dubbed *HymHub* and designed specifically to facilitate reproducible analysis of hymenotperan genomes.
The need for a more general solution motivated the development of GenHub in its current incarnation.
Rather than distributing processed data (which can occupy more than 1 GB of storage space per genome), GenHub provides portable code so that researchers can easily process reference genomes on their own computing resources.
This is all tied closely to our research philosophy and our conviction that published computational results (along with supporting software and data) should be reproducible and transparent.
More recently, we have implemented support for processing of user-supplied non-reference genomes.

- Built by Daniel Standage <daniel.standage@gmail.com>
- Development repository at https://github.com/standage/genhub
- [Installation instructions](docs/INSTALL.md)
- [User manual](docs/MANUAL.md)
- [Developer documentation](docs/DEVELOP.md)
- [GenHub code of conduct](docs/CONDUCT.md)

[travisbadge]: https://img.shields.io/travis/standage/genhub.svg
[pypiv]: https://img.shields.io/pypi/v/genhub.svg
[codecovbadge]: https://img.shields.io/codecov/c/github/standage/genhub.svg
[bsd]: https://img.shields.io/pypi/l/genhub.svg
