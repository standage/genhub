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

Additional Python modules are required for GenHub development: `pytest` and `coverage` (for automated unit tests), and `pep8` (for enforcing coding style).

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

### Configuration files

Information necessary for retrieving and processing reference genomes is stored in configuration files in YAML format.
In the source code distribution, these files are stored in the `genhub/genomes/` directory.
When installed via pip or from source, these files are copied to the `site-packages/genhub/genomes/` directory corresponding to the user-specified system-wide or virtual environment installation directory.

Creating a new configuration file for a genome stored in RefSeq or one of the other already supported databases should generally be straightforward.
Creating a new configuration for a genome from a new source will require the implementation of a new `GenomeDB` subclass: see below.

To create a new RefSeq YAML configuration, use the following protocol.

- Select a new 4-letter label for the genome.
  The convention is the first letter of the genus (upper case), followed by the first 3 letters of the species (lower case).
  This has not yet led to any collisions, so when possible follow this convention.
- Copy one of the existing GenHub `.yml` files with `source: refseq` and name the file using the new 4-letter label.
- Locate the desired assembly in the RefSeq FTP site.
  Starting at ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/, click on the appropriate clade (`invertebrate`, `vertebrate_mammal`, and so on) --> the species name --> `all_assembly_versions` --> the desired assembly version --> and then the file ending in `_assembly_stats.txt`.
  This file contains some information we'll need for the new YAML file.
- In the new YAML file, replace the label on the first line of the file with the new 4-letter label.
- Provide the name of the species using conventional binomial nomenclature.
  If there is a common name for the species, this should also be provided.
  Optionally, one or more labels indicating the clade(s) to which the species belongs can be provided, although this information is not yet used by GenHub.
- Make sure the **source** attribute is set to `refseq`.
- Set the **branch** attribute to the appropriate subdirectory of the RefSeq FTP root directory: `invertebrate`, `vertebrate_mammal`, and so on.
- Set the **accession** attribute to the **RefSeq assembly accession** specified in the `_assembly_stats.txt` file on the FTP site.
  This should begin with the letters `GCF`.
- Set the **build** attribute to the assembly name.
  Often it is sufficient to use the **Assembly name** attribute from the `_assembly_stats.txt` file, but if the assembly name contains spaces or non-standard characters, you'll need to double check the name of the file.
  The name will be of the format `GCF_xxxxxx.x_BUILD_assembly_stats.txt`, and the **build** attribute should in the new YAML file should be set to the value of the `BUILD` portion of the filename.
- If the assembly includes organellar genomes, you'll need to add the corresponding sequence IDs to the **annotfilter** and **seqfilter** attributes.
  See `Amel.yml` for an example.
  This attribute can also filter out problematic gene models or other genome features if needed.
  Simply provide a string that would filter these out of the GFF3 file *a la* `grep -v`.
- The **checksums** attribute contains a list of shasums for pre-processed data.
  You will not be able to fill this in until you have run the new configuration through the `prep` task.
  Once you have run `fidibus --relax prep` on the new configuration, examine and do some sanity checking on the pre-processed files `Xxxx.gdna.fa`, `Xxxx.gff3`, and `Xxxx.all.prot.fa`.
  If there are no apparent issues, compute checksums for these files using the `shasum` shell command and copy the checksums to the YAML file: **gdna** for the `Xxxx.gdna.fa` file's shasum, **gff3** for the `Xxxx.gff3` file's checksum, and **prot** for the `Xxxx.all.prot.fa` file's checksum.
  These checksums are used to verify the integrity of the data files and pre-processing on subsequent invokations of `Fidibus`: if the checksums don't match up, either the original data sources have changed, or the pre-processing procedure has changed.
  In either case, the data need to be re-examined to determine what the differences are.
  Often, minor updates to the RefSeq GFF3 file will simply require recomputing the checksum.
- Finally, provide a brief description of the genome assembly, annotation, and/or source.

You can drop this new YAML file into the `genhub/genomes/` directory, or you can specify an alternate directory with the `--cfgdir` setting.

### GenomeDB

The `genomedb` module implements a class for retrieving, processing, and managing data files.
The `GenomeDB` class is abstract, meaning that it defines some behavior shared by several subclasses and is not intended to be instantiated directly.
Processing that is specific to genomes from a particular source is implemented in various subclasses that extend the base `GenomeDB` class.

- `Am10DB`: this subclass is for the *Apis mellifera* genome, annotation version OGSv1.0.
- `BeeBaseDB`: this subclass is used for handling genomes listed as "BeeBase Consortium Data" at [HymenopteraBase](http://hymenopteragenome.org/).
- `CrgDB`: this subclass is used for handling two genomes published semi-officially to [a web page at the Centre de Regulacio Genomica](http://wasp.crg.eu/).
- `PdomDB`: this subclass is used for handling *Polistes dominula* data which, for much of GenHub's development, has had no formal distribution source.
- `RefSeqDB`: this subclass is used for handling genomes published in NCBI's RefSeq.
- `TairDB`: this subclass is for the *Arabidopsis thaliana* genome, version TAIR6.

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
All other scripts in the `scripts/` directory support this core program and are discussed briefly in the [user manual](MANUAL.md).
