check:
	python scripts/check.py

depend:
	@ pip install -r requirements.txt
	@ pip -m easy_install pyyaml

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
