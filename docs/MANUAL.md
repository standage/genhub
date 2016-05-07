GenHub Manual
=============

## Installation

See [the installation instructions](INSTALL.md) if you have not already installed GenHub and its dependencies.

## The `fidibus` program

The `fidibus` program is the primary user interface of the GenHub package.
For a complete listing of program options, execute `fidibus -h` in your shell.
The most important concepts are discussed below.

### Build tasks

The build program provides 6 primary build tasks.

- `download`: download the genome sequences, annotation, and protein sequences from the official source
- `format`: tidy up the primary data so that all data files, regardless of source, are in a common format
- `prepare`: extract sequences and parse annotations for various data types in preparation to calculate descriptive statistics
- `stats`: calculate descriptive statistics for the various data types
- `cleanup`: remove intermediate data files to reduce storage needs

A special build task, `list`, is provided for displaying all available genomes.

### Working directory

All data files downloaded and processed by GenHub are stored in a *working directory*.
This working directory includes additional dedicated sub-directories for each genome.
If the directory does not already exist, GenHub will create it for you.
Specify your desired working directory with the `--workdir` option (or `-w` for short).

### Parallel processing

Most modern computers, including desktops and laptops, have mutiple processors.
GenHub can utilize these processors to speed up computations.
Specify the number of processors you want to dedicate to GenHub with the `--numprocs` option (or `-p` for short).

### Some examples

Sometimes the best way to learn is to see some examples.

```
# Show all available genomes
genhub-build.py list

# Download the yeast genome, but do not process
genhub-build.py --workdir=/opt/data/myhub/ --genome=Scer download

# Download and process the Arabidopsis genome
genhub-build.py --workdir=/opt/data/myhub/ --genome=Scer download format prepare stats cleanup

# Retrieve several ant genomes
genhub-build.py --workdir=antgenomes/ --genome=Acep,Aech,Cbir,Cflo,Dqua,Lhum,Pbar,Sinv download format

# Retrieve a batch of honeybee genomes
genhub-build.py --workdir=./ --batch=honeybees download format prepare stats download format
```
