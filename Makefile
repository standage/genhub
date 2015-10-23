check:
	python scripts/check.py

depend:
	@ pip install -r requirements.txt
	@ pip -m easy_install pyyaml

test: genhub/conf.py genhub/ncbi.py
	@ nosetests -v --with-coverage --cover-package=genhub.conf,genhub.ncbi $^

style:
	@ pep8 genhub/*.py scripts/*.py

precommit: .git/hooks/pre-commit

.git/hooks/pre-commit:
	@ echo "pep8 genhub/*.py scripts/*.py" > $@
	@ chmod 755 $@

version:
	python setup.py version

clean:
	rm -f *.pyc genhub/*.pyc
