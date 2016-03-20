*Daphnia pulex* configuration
=============================

GenHub includes a module and a recipe configuration for the genome of the water flea *Daphnia pulex*.
The data for *D. pulex* are publicly available from the DOE JGI (see http://genome.jgi.doe.gov/Dappu1/Dappu1.download.ftp.html), but unfortunately they require user registration.
This makes automated data retrieval impractical, and invoking the `genhub-build.py download` task on Dpul will elicit an error.
Analyzing the *D. pulex* data with GenHub requires that the user download the data files manually.

With `./species/` as the working directory, execute the following commands after downloading the files to the current directory.

```bash
mkdir species/Dpul/
mv Daphnia_pulex.fasta.gz FrozenGeneCatalog20110204.gff3.gz FrozenGeneCatalog20110204.proteins.fasta.gz species/Dpul
gunzip species/Dpul/*.gz
```

All subsequent build tasks (`format`, `prepare`, etc.) should work correctly from this point.
