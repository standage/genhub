Installing GenHub
=================

The installation of the GenHub package itself should be pretty painless.
The easiest way to install is with `pip`.

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

To install the latest unreleased version, pip can install directly from GitHub.

```bash
pip install git+https://github.com/standage/genhub.git
```

All of these methods will also automatically install the `pyyaml` and `pycurl` dependencies.
See below if you have trouble installing `pycurl` in a virtual environment.



## External software

GenHub is implemented in Python and does not need to be compiled.
However, it does depend on a few external software packages that do need to be compiled.
The required packages must be installed before you can run GenHub.
The optional packages are only required for the specified features.

- required packages
    - the [GenomeTools library][gt] ([installation instructions][gt-install]), version 1.5.8 or higher
    - the [AEGeAn Toolkit][agn] ([installation instructions][agn-install]), version 0.16.0 or higher
        - be sure to run `make install-scripts` or add AEGeAn's `data/scripts/` directory to your `$PATH` as part of your setup
- optional packages
    - the [CD-HIT package][cdhit] ([installation instructions][cdhit-install]), tested with version 4.6.4;
      required only for the `cluster` build task
    - the [pandas][pandas] data analysis library ([installation instructions][pandas-install]);
      required only for data summary scripts

If installing from source, you can invoke `make check` from the GenHub root directory to check whether all software prerequisites have been satisfied.

## Troubleshooting PycURL installation

On some systems installing the PycURL dependency may require an additional step or two.

- If you are having issues installing PycURL in a [virtual environment][venv], try the [following workaround][curl]: deactivate the virtualenv, install PycURL system-wide (or in a directory you control), and then copy the `pycurl` files into your virtualenv site-packages.
- If you are on a Fedora machine and lack administrative privileges, you may need to execute `export PYCURL_SSL_LIBRARY=nss` before installing PycURL. See [this page][pycurl_ssl] for more information.


[gt]: https://github.com/genometools/genometools
[gt-install]: https://github.com/genometools/genometools
[agn]: http://standage.github.io/AEGeAn
[agn-install]: http://aegean.readthedocs.org/
[cdhit]: http://weizhongli-lab.org/cd-hit/
[cdhit-install]: http://weizhongli-lab.org/cd-hit/download.php
[pandas]: http://pandas.pydata.org/
[pandas-install]: http://pandas.pydata.org/pandas-docs/stable/install.html
[venv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[curl]: http://eon01.com/blog/hacking-pycurl-installation-problem-within-virtualenv/
[pycurl_ssl]: http://pycurl.sourceforge.net/doc/install.html#pip-and-cached-pycurl-package
[rel]: https://github.com/standage/genhub/releases
