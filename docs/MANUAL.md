GenHub Manual
=============

## Summary

GenHub is a companion to the [AEGeAn Toolkit](agn) and provides a framework for analysis of eukaryotic genome composition and organization.
GenHub calculates a variety of statistics on *interval loci (iLoci)* computed from user-supplied genome data.
It can also retrieve reference genomes directly from public databases (such as NCBI RefSeq) for easily reproducible comparative analyses.

GenHub is free for use under a permissive open source [license](LICENSE.txt).

## LocusPocus Fidibus!

The AEGeAn Toolkit provides `LocusPocus`, a basic program for computing iLoci from a genome annotation.
The `Fidibus` program from GenHub provides a more comprehensive pipeline around `LocusPocus`, integrating genome and protein sequences and performing additional pre-processing, post-processing, error-checking, and calculation of summary statistics for iLoci and additional genome features.

Each iLocus captures the genomic context of a single gene, a group of overlapping genes, or an intergenic region.
iLoci provide a detailed and granular representation of the entire genome that is robust to improvements to the assembly and annotation.
See our upcoming paper (Standage and Brendel, 2016) for more information.

## Installation

See [the installation instructions](INSTALL.md) if you have not already installed GenHub and its dependencies.

## The `fidibus` program

The `fidibus` program is the primary user interface of the GenHub package.
For a complete listing of program options, execute `fidibus -h` in your shell.
The most important concepts are discussed below.

### Build tasks

The build program provides 6 primary build tasks.

- `download`: download the reference genome sequence, annotation, and protein sequences from the official source; in the case of user-supplied genomes on the local file system, verify that the specified files exist
- `prep`: pre-process the primary data, tidying it up so that all data files, regardless of source, are in a common format
- `iloci`: compute iLoci and extract iLocus sequences
- `breakdown`: extract sequences and parse annotations for various genome features to facilitate calculating descriptive statistics
- `stats`: calculate descriptive statistics for various genome features
- `cleanup`: remove intermediate data files to reduce storage needs

A special build task, `list`, is provided for displaying all available reference genomes.

### Working directory

All data files downloaded and processed by `fidibus` are stored in a *working directory*.
Each genome data set has a dedicated sub-directory in the working directory, named with a unique (typically four-letter) label.
If the working directory does not already exist, `fidibus` will create it.
Specify your desired working directory with the `--workdir` option (or `-w` for short).

### Parallel processing

Most modern computers, including desktops and laptops, have mutiple processors.
The `fidibus` program can utilize these processors to speed up computations.
Specify the number of processors you want to dedicate to GenHub with the `--numprocs` option (or `-p` for short).

### Some examples

Sometimes the best way to learn is to see some examples.

```
# Show all available reference genomes
fidibus list

# Download the budding yeast genome, but do not process
fidibus --workdir=/opt/data/genomes/ --refr=Scer download

# Download and process the Arabidopsis genome
fidibus --workdir=/opt/data/genomes/ --genome=Atha download prep iloci breakdown stats cleanup

# Retrieve and pre-process several ant genomes
fidibus --workdir=antgenomes/ --genome=Acep,Aech,Cbir,Cflo,Dqua,Lhum,Pbar,Sinv download prep

# Retrieve and process a batch of honeybee genomes
fidibus --workdir=./ --batch=honeybees download prep iloci breakdown stats
```

## Supporting scripts

More info coming soon.
For now, see https://github.com/BrendelGroup/IntervalLoci.
