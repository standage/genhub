GenHub Manual
=============

## Introduction

GenHub is a free open-source software framework for analyzing eukaryotic genomes, computing and reporting a variety of statistics reflecting genome content and organization.
GenHub works with user-supplied genomes (in Fasta and GFF3 format), and can also retrieve dozens of reference genomes from NCBI RefSeq and other public databases for comparison.

The *interval locus* (*iLocus*) is the primary unit of organization in GenHub.
Each iLocus captures the genomic context of a single gene, a group of overlapping genes, or an intergenic region.
iLoci provide a detailed and granular representation of the entire genome that is robust to improvements to the assembly and annotation.
See our upcoming paper (Standage and Brendel, 2016) for more information.


## Installation

See [the complete installation instructions](INSTALL.md) if you have not already installed GenHub and its dependencies.


## The `Fidibus` program

### LocusPocus Fidibus!

The `Fidibus` program is the primary user interface of the GenHub package.
It is a companion to the `LocusPocus` program included in the [AEGeAn Toolkit](https://brendelgroup.github.io/AEGeAn), which computes iLoci from a user-supplied genome annotation in GFF3 format.
`Fidibus` provides a comprehensive pipeline around `LocusPocus`, integrating genome and protein sequences and performing additional pre-processing, post-processing, error-checking, and calculation of summary statistics for iLoci and additional genome features.

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

### Parallel processing

Most modern computers, including desktops and laptops, have mutiple processors.
When analyzing multiple genomes, the `fidibus` program can utilize these processors to speed up computations by processing multiple genomes simultaneously on different threads.
Specify the number of processors you want to dedicate to GenHub with the `--numprocs` option (or `-p` for short).

### Some examples

Sometimes the best way to learn is to see some examples.

```bash
# Show all available reference genomes
fidibus list

# Download the budding yeast genome, but do not process
fidibus --workdir=/opt/data/genomes/ --refr=Scer download

# Download and process the Arabidopsis genome
fidibus --workdir=/opt/data/genomes/ --genome=Atha \
        download prep iloci breakdown stats cleanup

# Retrieve and pre-process several ant genomes
fidibus --workdir=antgenomes/ --genome=Acep,Aech,Cbir,Cflo,Dqua,Lhum,Pbar,Sinv \
        download prep

# Retrieve and process a batch of honeybee genomes
fidibus --workdir=./ --batch=honeybees download prep iloci breakdown stats
```


## Working directory

All data files produced or downloaded by `Fidibus` are stored in a *working directory*.
If the working directory does not already exist, `Fidibus` will create it.
Specify your desired working directory with the `--workdir` option (or `-w` for short).

### Directory structure

Each genome data set has a dedicated sub-directory in the working directory, named with a unique (typically four-letter) label.
Consider the following example.

```
fidibus --workdir=demo --refr=Otau,Oluc download prep
```
This command will download and pre-process genomes for two species (green algae, in this case).
The resulting files and directories will be organized as follows.

```
demo/
├── Oluc/
│   ├── GCF_000092065.1_ASM9206v1_genomic.fna.gz
│   ├── GCF_000092065.1_ASM9206v1_genomic.gff.gz
│   ├── GCF_000092065.1_ASM9206v1_protein.faa.gz
│   ├── Oluc.all.prot.fa
│   ├── Oluc.gdna.fa
│   └── Oluc.gff3
└── Otau/
    ├── GCF_000214015.2_version_050606_genomic.fna.gz
    ├── GCF_000214015.2_version_050606_genomic.gff.gz
    ├── GCF_000214015.2_version_050606_protein.faa.gz
    ├── Otau.all.prot.fa
    ├── Otau.gdna.fa
    └── Otau.gff3
```

The files beginning with `GCF` were downloaded directly from the RefSeq database.
The other files comprise genome sequences, genome annotations, and protein sequences that have been pre-processed and are ready for parsing into iLoci.

### Directory contents

Running the complete `Fidibus` pipeline will produce dozens of data files in each dedicated genome directory.
These include the following.

- unprocessed data files downloaded directly from public databases (in the case of reference genomes)
    - usually compressed
    - start with `GCF` in the case of RefSeq genomes
- pre-processed genome data
    - genome sequences (`Xxxx.gdna.fa`)
    - genome annotation (`Xxxx.gff3`)
    - protein sequences (`Xxxx.all.prot.fa`)
- iLoci
    - locations (`Xxxx.iloci.gff3`)
    - sequences (`Xxxx.iloci.fa`)
    - merged iLocus data (`Xxxx.miloci.gff3` and `Xxxx.miloci.fa`)
    - genome annotation, 1 gene model per iLocus (`Xxxx.ilocus.mrnas.gff3`)
    - non-redundant protein sequences, 1 gene model per iLocus (`Xxxx.prot.fa`)
- tables of descriptive statistics easily loaded into R/Python data frames for analysis
    - iLoci (`Xxxx.iloci.tsv`)
    - merged iLoci (`Xxxx.miloci.tsv`)
    - gene models (`Xxxx.pre-mrnas.tsv`)
    - mature mRNAs (`Xxxx.mrnas.tsv`)
    - exons (`Xxxx.exons.tsv`)
    - introns (`Xxxx.introns.tsv`)
    - coding sequences (`Xxxx.cds.tsv`)
- various other intermediate or ancillary files


## Supporting scripts

Only a brief summary of each script is provided below.
For additional documentation demonstrating how these scripts were used to produce the results reported in (Standage and Brendel, 2016), see https://github.com/BrendelGroup/IntervalLoci.

- pipeline scripts (invoked by `Fidibus`)
    - `genhub-filens.py`: report lengths of flanking iiLoci for each giLocus
    - `genhub-format-gff3.py`: perform various annotation pre-processing tasks
    - `genhub-glean-to-gff3.py`: convert GLEAN output to GFF3
    - `genhub-namedup.py`: copy GFF3 `ID` attributes to `Name` attributes
    - `genhub-stats.py`: calculate descriptive statistics for various data types
- post-pipeline scripts (invoked by user)
    - `genhub-compact.py`: compute (φ, σ) meaures of genome compactness
    - `genhub-ilocus-summary.py`: compute summary table of iLocus data
    - `genhub-milocus-summary.py`: compute summary table of merged iLocus data
    - `genhub-pilocus-summary.py`: compute summary table of protein-coding iLocus data
