GenHub
======

GenHub is software for managing your own hub of annotated genome assemblies. It
comes configured with simple recipes to collect and standardize data from a
variety of sources, and it is easy to extend with recipes for additional data.

* Built by Daniel Standage <daniel.standage@gmail.com>
* Available at https://github.com/standage/genhub

## Obtaining GenHub

The easiest way to obtain the latest and greatest version of GenHub is to clone
the git repository.

```
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

[rel]: https://github.com/standage/genhub/releases

## Prerequistes

GenHub is implemented primarily in Python, and should be compatible with Python
2.7+ and Python 3.3+. In addition to the Python packages listed in
`requirements.txt` file, GenHub depends on the [GenomeTools library][gt] and
the [AEGEan toolkit][agn]. Running `make depend` with administrative privileges
or within a user-controlled [virtual environment][venv] will install the
prerequisite Python packages, and installation instructions for GenomeTools and
AEGeAn are available from the corresponding source code distributions.

**Special note about PycURL**: There appear to be some issues installing PycURL
in a virtual environment. If you are having issues installing PycURL, the
[following workaround][curl] worked for me: deactivate the virtualenv, install
PycURL system-wide (or in a directory you control), and then copy the pycurl
files into your virtualenv site-packages.

[gt]: http://genometools.org
[agn]: http://standage.github.io/AEGeAn
[venv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[curl]: http://eon01.com/blog/hacking-pycurl-installation-problem-within-virtualenv/

## Overview

More soon!

## Running a build

More soon!
