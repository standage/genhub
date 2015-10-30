check:
	python scripts/genhub-check.py

check-dev:
	python scripts/genhub-check.py --dev

depend:
	@ pip install --upgrade pip
	@ pip install -r requirements.txt
	@ python -m easy_install pyyaml

test:
	@ rm -f .coverage
	@ nosetests -v --with-coverage --cover-package=genhub genhub/*.py

style:
	@ pep8 genhub/*.py scripts/*.py

precommit: .git/hooks/pre-commit

.git/hooks/pre-commit:
	@ echo "pep8 genhub/*.py scripts/*.py" > $@
	@ chmod 755 $@

version:
	python setup.py version

clean:
	rm -rf *.pyc genhub/*.pyc .coverage testdata/scratch/*
