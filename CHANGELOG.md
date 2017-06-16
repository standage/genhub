# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added
- A `relax` option to `fidibus` to proceed with prep task despite failed shasum verification.
- The `*.protein2ilocus.repr.tsv` file containing mapping for iLocus representatives only.
- Better exception handling/reporting for failed downloads.
- Reference genome configurations for *Zootermopsis nevadensis* (in support of the BWASP project) and *Orchesella cincta* (as additional proof-of-concept).
- Support for all Genbank genomes, not just those within RefSeq.
- Restored support for HymenopteraBase versions of several ant genomes.

### Changed
- Ancillary files `.ilocus.mrnas.txt` and `.protein2ilocus.txt` are not `.tsv` files with headers.
- Extensive documentation updates.
- Switched from nose to py.test as the testing framework.
- Updated checksums for many NCBI annotations to compensate for, among other things:
    - changes in `##species` pragmas
    - transcript evidence descriptions and other metadata
    - feature types for annotated mobile elements, antisense transcripts, origins of replication, and various other features
    - an update to the *C. elegans* annotation (< 1% gene models affected)
    - an update to the *D. rerio* annotation (≈ 3% CDS exons, ≈ 10% all exons affected)
    - an update to the *M. musculus* annotation (1% CDS exons, 5% of all exons affected)

### Removed
- Deprecated `genhub-fix-trna.py` script.

## [0.4.0] - 2016-05-09

### Changed
- The `genhub-build.py` script is now `fidibus`, and the CLI was updated.
- Pdom, Pcan, and Dqua now default to RefSeq genomes, with Toth Lab and CRG genomes available under labels Pdtl, Pccr, and Dqcr.

### Fixed
- The `cluster` build task now uses `-M 0` by default.
- The `Registry` class was simplified.

### Added
- The build script (now `fidibus`) now has support for custom genomes.
- Sequence IDs are now reported for iLocus and miLocus tables.
- New script for creating a piLocus summary table.
- Recipes for chick pea, cabbage, and soybean.
- Recipes for another mosquito (*Aedes aegypti*) and a spider mite (non-insect arthropod).
- A `--shuffled` option to several scripts for reading from `*iloci.shuffled.tsv`, and improved access from the GenomeDB class.

## [0.3.7] - 2016-03-19
### Fixed
- Correctly included missing script in `setup.py`.

## [0.3.6] - 2016-03-19
### Added
- New recipe for cotton.
- New recipe for *Daphnia pulex*.
- New script for creating an iLocus summary table.

## [0.3.5] - 2016-03-17
### Fixed
- Updated test data files to compensate for corrections to LocusPocus' reporting of iLocus type.

## [0.3.4] - 2016-03-16
### Added
- Added `seqfilter` to RefSeq module and .yaml configs.

### Fixed
- Used new `seqfilter` mechanism to eliminate redundant patch and variant data from human and mouse genomes.
- Updated rice recipe following an update to the corresponding RefSeq entry.

## [0.3.3] - 2016-03-03
### Fixed
- Filled out partial implementation of `--delta` option for the build script.

## [0.3.2] - 2016-03-02
### Fixed
- Removed gene model with overlapping exons causing processing issues in *C. reinhardtii*.

## [0.3.1] - 2016-02-24
### Fixed
- Removed unnecessary `Fragment` column from `.iloci.tsv` table. Redundant with `LocusClass=fiLocus`.
- Removed outdated code for computing `LocusClass`.
- Fixed feature for specifying iLocus label format.

## [0.3.0] - 2016-02-24
### Added
- Integration with codecov.io.
- Lots of genome recipes
    - *Anopheles gambiae*
    - *Homo sapiens*
    - *Theobroma cacao*
    - some version-specific recipes
        - TAIR6
        - *Apis mellifera* assembly 2.0 / OGS 1.0
        - *Apis mellifera* assembly 4.5 / OGS 3.2
    - 9 species of green algae
- Implemented the `cleanup` and `cluster` tasks for the main build script.

### Changed
- Unit test fixtures to account for AEGeAn's improved reporting of iLocus types.
- Protein checksum for *Xenopus tropicals*, which was recently updated to drop the *Silurana* designation.

## [0.2.1] - 2016-01-15
### Fixed
- versioneer issue with MANIFEST

## [0.2.0] - 2016-01-15
### Added
- Recipe for the rice genome (*Oryza sativa* L. ssp. *japonica*).
- Recipe for a model legume genome (*Medicago truncatula*).
- Batch for all Hymenoptera.
- Multiprocessing support for build script.

### Changed
- Complete overhaul of the genome configuration handling (now in the `registry` module).
- Minor changes to the Travis CI configuration.
- Excluded *Danio rerio* config from CI tests, as its resource requirements are right at the limit of what the Travis VMs can handle.
- Updated *Xenopus tropicalis* config to drop the parentheses in the species name.
- Updated *Drosophila melanogaster* config to the latest RefSeq assembly/annotation.
- Moved sha1 and file resolution code from `__init__.py` to `GenomeDB` class.

## [0.1.2] - 2016-01-09
### Added
- Package metadata.

### Fixed
- Minor improvements to documentation.

## [0.1.1] - 2016-01-08
### Fixed
- Added pre-requisites to setup.py.

## [0.1.0] - 2016-01-08

### Added
- first stable release!
- `GenomeDB` class and various extensions for downloading and formatting data.
- Modules for parsing and describing iLoci, proteins, mRNAs, exons, introns, and coding sequences.
- The script implementing the `stats` task, brought over with minimal changes from HymHub.
- Unit tests, with 100% success rate and 100% coverage of core package code (not scripts yet).
- Minimal installation and usage documentation.
