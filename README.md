GenHub
======

## Summary

GenHub is software for managing a hub of annotated genome assemblies.
It comes configured with simple recipes to collect and standardize genome data from a variety of sources, and it is easy to extend with recipes for additional data.
The interval locus (iLocus) is the primary unit of organization: see the documentation for the [AEGeAn Toolkit][agn_rtd] for more information.

GenHub is primarily designed as a data distribution and reproducibility mechanism.
Because each processed data set includes many non-standard files and occupies >1 gigabyte of storage space (>10G for mammals), finding stable public long-term storage is problematic.
So rather than distributing the processed data itself, GenHub distributes stable code that enables the user to retrieve, process, and store the data using their own computing resources.

## Obtaining GenHub

The easiest way to obtain the latest and greatest version of GenHub is to clone the development repository from GitHub.

```bash
git clone https://github.com/standage/genhub.git
cd genhub
make check
```

Another option is to download a stable version from the [release listing][rel].

```bash
# replace x.y.z with an actual version
wget https://github.com/standage/genhub/archive/x.y.z.tar.gz
tar -xzf x.y.z.tar.gz
cd genhub-x.y.z
make check
```

Whichever you choose, be sure to check that all of GenHub's [prerequisites](docs/INSTALL.md) are installed on your system.

## Additional Details

GenHub was originally dubbed *HymHub* and was designed specifically for managing hymenotperan genomes.
The need for a more general solution motivated the development of GenHub in its current incarnation.

- Built by Daniel Standage <daniel.standage@gmail.com>
- Available at https://github.com/standage/genhub
- [![GenHub build status][travisbadge]](https://travis-ci.org/standage/genhub)


[travisbadge]: https://travis-ci.org/standage/genhub.png
[agn_rtd]: http://aegean.readthedocs.org
[rel]: https://github.com/standage/genhub/releases