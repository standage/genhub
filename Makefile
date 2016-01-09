shufcmd := $(shell which shuf || which gshuf)
SHELL := bash
SHELLOPTS := errexit:pipefail

check:
	python dev/check.py

check-dev:
	python dev/check.py --dev

depend:
	@ pip install --upgrade pip
	@ pip install -r requirements.txt
	@ python -m easy_install pyyaml

test:
	@ rm -f .coverage
	@ nosetests -v --with-coverage --cover-package=genhub genhub/*.py

testmore:
	@ set -e && for conf in $$(find conf -type f -name "????.yml" | grep -v -e Mmus -e Btau -e Emex | $(shufcmd) | head -2); do echo $$conf; genhub-build.py --cfg $$conf --workdir scratch/testmore/ download format prepare stats; rm -r scratch/testmore/; done

style:
	@ pep8 genhub/*.py scripts/*.py

precommit: .git/hooks/pre-commit

.git/hooks/pre-commit:
	@ echo "pep8 genhub/*.py scripts/*.py" > $@
	@ chmod 755 $@

version:
	python setup.py version

pypi:
	python setup.py sdist upload

clean:
	rm -rf *.pyc genhub/*.pyc .coverage testdata/scratch/*
