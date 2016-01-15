Installing GenHub
=================

Installing GenHub itself is pretty painless.
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

Either of these methods will install the `pyyaml` and `pycurl` dependencies.
See below if you have trouble installing `pycurl` in a virtual environment.

## Third-party software

GenHub is implemented primarily in Python, and should be compatible with Python 2.7 and Python 3.3+.
The GenHub code itself does not need to be compiled.
However, it does depend on two third-party libraries that do need to be compiled.
Links to these libraries (and corresponding installation instructions) are provided below.

- the [GenomeTools library][gt] ([installation][gt-install])
- the [AEGeAn Toolkit][agn] ([installation][agn-install])

## Troubleshooting PycURL installation

On some systems installing the PycURL dependency may require an additional step or two.

- If you are having issues installing PycURL in a [virtual environment][venv], try the [following workaround][curl]: deactivate the virtualenv, install PycURL system-wide (or in a directory you control), and then copy the `pycurl` files into your virtualenv site-packages.
- If you are on a Fedora machine and lack administrative privileges, you may need to execute `export PYCURL_SSL_LIBRARY=nss` before installing PycURL. See [this page][pycurl_ssl] for more information.


[gt]: https://github.com/genometools/genometools
[gt-install]: https://github.com/genometools/genometools
[agn-install]: http://aegean.readthedocs.org/
[agn]: http://standage.github.io/AEGeAn
[venv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[curl]: http://eon01.com/blog/hacking-pycurl-installation-problem-within-virtualenv/
[pycurl_ssl]: http://pycurl.sourceforge.net/doc/install.html#pip-and-cached-pycurl-package
[rel]: https://github.com/standage/genhub/releases
