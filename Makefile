shufcmd := $(shell which shuf || which gshuf)
SHELL := bash
SHELLOPTS := errexit:pipefail

check:
	@ python dev/check.py

test:
	@ rm -f .coverage
	@ pytest --cov=genhub/ genhub/*.py

testmore:
	@ set -e && for conf in $$(ls genhub/genomes/*.yml | grep -v -e Mmus -e Btau -e Emex -e Drer -e Hsap | $(shufcmd) | head -2); do label=$$(basename $$conf .yml); echo $$label; fidibus --refr=$$label --workdir=scratch/testmore/ --relax download prep iloci breakdown stats; rm -r scratch/testmore/; done

style:
	@ pycodestyle genhub/*.py scripts/*.py

devdeps:
	pip install --upgrade pycodestyle pytest pytest-cov pep8 coverage codecov

devhooks: .git/hooks/pre-commit

.git/hooks/pre-commit:
	@ echo "make style" > $@
	@ chmod 755 $@

version:
	python setup.py version

pypi:
	python setup.py sdist upload

clean:
	rm -rf *.pyc genhub/*.pyc .coverage testdata/scratch/* build/ dist/ genhub.egg-info/ __pycache__/
