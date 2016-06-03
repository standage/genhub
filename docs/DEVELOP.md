GenHub Development
==================

## Introduction

As of yet, GenHub development has essentially been a one-man show.
Early versions of this software were written in support of a specific research project.
As the needs of that project and related projects grew, the need for more robust software (and concomitantly a more robust development process) emerged.
GenHub in its current incarnation is a more generalized and sturdy solution to those original research problems.

I have found GenHub very useful in my own research, and my hope is that others will find it useful as well.
The software was intentionally designed to be extensible, and I would be thrilled to integrate contributions if you have extended GenHub to make it more useful for you.
This developer documentation is written as a reference for anyone who might be interested in understanding how GenHub is implemented.
And regardless of whether GenHub ever garners wider interest, this documentation also serves as a personal record and is a key component in my effort to make my research more reproducible and transparent.

## Implementation

GenHub is implemented in the [Python programming language](https://www.python.org/), and is compatible with Python 2.7 and Python 3.3 or newer.

### Dependencies

GenHub delegates many processing tasks to external programs from the [GenomeTools library](http://genometools.org) and the [AEGeAn Toolkit](http://brendelgroup.github.io/AEGeAn/).
These software packages must be installed on your system before you can run or develop GenHub.

GenHub also depends on several Python modules.
The `pyyaml` and `pycurl` modules are required for runtime, and should be installed automatically when installing GenHub from PyPI (`pip install genhub`) or from source (`python setupy.py install`).
See [INSTALL.md](INSTALL.md) for more information.

Additional Python modules are required for GenHub development: `nose` and `coverage` (for automated unit tests), and `pep8` (for enforcing coding style).

### Distribution

The source code, test data, and other supporting files have been organized to facilitate GenHub's distribution as a [Python package](https://docs.python.org/3/tutorial/modules.html#packages).
When installed on a user's system, the core GenHub modules and scripts are copied to a dedicated location where they can be found by Python and the user's `PATH`, respectively.

## Getting started

The following is suggested for setting up a GenHub development environment.

- Fork the main GenHub repository on GitHub
- Clone (make a local copy of) your fork to your system: `git clone https://github.com/yourusername/genhub.git && cd genhub`
- Set up a style check that will run before each attempt to store a new commit: `echo 'pep8 genhub/*.py scripts/*.py' > ~/.git/hooks/pre-commit`
- Add the GenHub root directory to your `PYTHONPATH` variable: `export PYTHONPATH=$(pwd)`
- Add the GenHub `scripts` directory to your `PATH` variable: `export PATH=$(pwd)/scripts:$PATH`
- Verify that GenomeTools and AEGeAn are installed correctly: `make check`
- Run the test suite: `make test`

If everything looks good up to this point, you're ready to go!

## GenHub components

### Registry

The `registry` module implements a class for managing reference genome configurations.

- A *genome configuration* is data in YAML format containing metadata about an annotated genome: specifically, the information needed to download and pre-process the genome sequence, the genome annotation, and the protein sequences.
- A *batch configuration* is data in plain text format containing labels for a set of related genome configurations.
  Batch configurations facilitate batch processing of multiple (usually related) genomes.

A couple of registry objects are stored in the `genhub` package's global space for use as unit testing fixtures.
These are not intended to be accessed by end-user-facing code.

### GenomeDB

The `genomedb` module implements a class for retrieving, processing, and managing data files.
The `GenomeDB` class is abstract, meaning that it defines some behavior shared by several subclasses and is not intended to be instantiated directly.
Processing that is specific to genomes from a particular source is implemented in various subclasses that extend the base `GenomeDB` class.

- `BeeBase`: this subclass is used for handling genomes listed as "BeeBase Consortium Data" at [HymenopteraBase](http://hymenopteragenome.org/).
- `CRG`: this subclass is used for handling two genomes published semi-officially to [a web page at the Centre de Regulacio Genomica](http://wasp.crg.eu/).
  The GenBank and RefSeq FTP sites have since been streamlined, but this class has been kept for sake of reproducibility (the old FlyBase data is still available in the FTP archives).
- `PdomDB`: this subclass is used for handling *Polistes dominula* data which, for much of GenHub's development, has had no formal distribution source.
- `RefSeqDB`: this subclass is used for handling genomes published in NCBI's RefSeq.

Genome configurations and the `GenomeDB` classes work closely together: each subclass implements the procedures needed to download and process data from a particular source, and the genome configuration provides details for downloading a specific data set.

The `GenericDB` class handles user-supplied custom genome data sets.

### Feature type modules

Several modules are provided for handling and describing various genome features types once the sequences and annotations have been downloaded and properly formatted.

- `iloci`: this module is for handling interval loci (iLoci), the primary organizational unit of GenHub.
  Each iLocus represents the genomic context of a single gene, a set of overlapping genes, or an intergenic region.
  For more information, see the [AEGeAn Toolkit documentation](http://aegean.readthedocs.org/en/latest/loci.html).
- `mrnas`: this module is for handling pre-mRNAs and mature (spliced) mRNAs.
- `exons`: this module is for handling exons, coding sequences, and introns.
- `proteins`: this module is for handling proteins.

In this context, *handling* means managing sequences, parsing annotations, and determining the relationship between features of these various types.

### Utility modules

- `fasta`: read, write, and subset sequences in Fasta format.
- `download`: retrieve remote data using cURL.
- `_version.py`: third-party module ([Versioneer](https://github.com/warner/python-versioneer)) for inferring the version number from the git or package environment.

### Build script (and other scripts)

The `fidibus` script implements the primary end-user interface to GenHub.
All other scripts in the `scripts/` directory support this core program and will not be discussed in depth here.
