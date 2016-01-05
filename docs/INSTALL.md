Installing GenHub
=================

## Prerequistes

Before getting started with GenHub, make sure that all prerequisites are installed on your system.
This includes the following.

- A UNIX operating system (Mac OS X or Linux should work fine)
- Basic build tools like `gcc` and `make`
- the Python packages specified in `requirements.txt`
- the [GenomeTools library][gt]
- the [AEGeAn Toolkit][agn]

Running `make depend` with administrative privileges or within a user-controlled [virtual environment][venv] will install the prerequisite Python packages.
Installation instructions for GenomeTools and AEGeAn are available from the corresponding source code distributions.

## Installing GenHub

GenHub is implemented primarily in Python, and should be compatible with Python 2.7 and Python 3.3+.
The GenHub code itself does not need to be compiled.
Eventually GenHub will be registered with the Python Package Index (so you can `pip install genhub`), but for now running GenHub directly from the development directory is recommended.
Set your `PATH` and `PYTHONPATH` variables so that the operating system can find the GenHub scripts and modules, and then use the `check-dev` task to troubleshoot installation of prerequisites.

```
export PATH=$(pwd)/scripts:$PATH
export PYTHONPATH=$(pwd)
make check-dev
```

## Special note about PycURL

In the past there were some issues installing PycURL in a virtual environment.
If you are having issues installing PycURL, try the [following workaround][curl]: deactivate the virtualenv, install PycURL system-wide (or in a directory you control), and then copy the pycurl files into your virtualenv site-packages.


[gt]: http://genometools.org
[agn]: http://standage.github.io/AEGeAn
[venv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[curl]: http://eon01.com/blog/hacking-pycurl-installation-problem-within-virtualenv/
