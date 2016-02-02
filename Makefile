shufcmd := $(shell which shuf || which gshuf)
SHELL := bash
SHELLOPTS := errexit:pipefail

check:
	@ python dev/check.py

test:
	@ rm -f .coverage
	@ nosetests -v --with-coverage --cover-package=genhub genhub/*.py

testmore:
	@ set -e && for conf in $$(ls genhub/genomes/*.yml | grep -v -e Mmus -e Btau -e Emex -e Drer -e Hsap | $(shufcmd) | head -2); do label=$$(basename $$conf .yml); echo $$label; genhub-build.py --genome $$label --workdir scratch/testmore/ download format prepare stats; rm -r scratch/testmore/; done

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
	rm -rf *.pyc genhub/*.pyc .coverage testdata/scratch/* build/ dist/ genhub.egg-info/ __pycache__/
