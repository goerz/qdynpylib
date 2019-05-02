.PHONY: black black-check clean clean-build clean-pyc clean-test clean-venvs coverage develop develop-docs develop-test dist dist-check docs help install isort isort-check jupyter-lab jupyter-notebook flake8-check pylint-check notebooks pre-commit-hooks release spellcheck test test-upload uninstall upload
.DEFAULT_GOAL := help
CONDA_PACKAGES = qutip
TESTENV = MATPLOTLIBRC=tests
TESTOPTIONS = --doctest-modules --cov=qdyn --nbval --sanitize-with docs/nbval_sanitize.cfg
TESTS = src tests docs/*.rst
# if there are any ipynb files added to the documentation, make sure to extend
# the above list of TESTS
BLACKOPTIONS = --skip-string-normalization --line-length 79
LATESTVENV = .venv/py37


define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-z0-9A-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:  ## show this help
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-venvs ## remove all build, test, coverage, and Python artifacts, as well as environments
	$(MAKE) -C docs clean

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr src/*.egg-info
	rm -fr pip-wheel-metadata
	find tests src -name '*.egg-info' -exec rm -fr {} +
	find tests src -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find tests src -name '*.pyc' -exec rm -f {} +
	find tests src -name '*.pyo' -exec rm -f {} +
	find tests src -name '*~' -exec rm -f {} +
	find tests src -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/

clean-venvs: ## remove testing/build environments
	rm -fr .tox
	rm -fr .venv

flake8-check: $(LATESTVENV)/bin/python ## check style with flake8
	$(LATESTVENV)/bin/python -m flake8 src tests

pylint-check: $(LATESTVENV)/bin/python ## check style with pylint
	$(LATESTVENV)/bin/python -m pylint -j 0 src


test: test36 test37  ## run tests on every supported Python version

.venv/py34/bin/py.test:
	@conda create -y -m -p .venv/py34 python=3.4
	@# if the conda installation does not work, simply comment out the following line, and let pip handle it
	@conda install -y --override-channels -c defaults -c conda-forge -p .venv/py34 $(CONDA_PACKAGES)
	@.venv/py34/bin/python -m pip install -e .[dev]

test34: .venv/py34/bin/py.test ## run tests for Python 3.4
	$(TESTENV) $< -v $(TESTOPTIONS) $(TESTS)

.venv/py35/bin/py.test:
	@conda create -y -m -p .venv/py35 python=3.5
	@# if the conda installation does not work, simply comment out the following line, and let pip handle it
	@conda install -y --override-channels -c defaults -c conda-forge -p .venv/py35 $(CONDA_PACKAGES)
	@.venv/py35/bin/python -m pip install -e .[dev]

test35: .venv/py35/bin/py.test ## run tests for Python 3.5
	$(TESTENV) $< -v $(TESTOPTIONS) $(TESTS)

.venv/py36/bin/py.test:
	@conda create -y -m -p .venv/py36 python=3.6
	@# if the conda installation does not work, simply comment out the following line, and let pip handle it
	@conda install -y --override-channels -c defaults -c conda-forge -p .venv/py36 $(CONDA_PACKAGES)
	@.venv/py36/bin/python -m pip install -e .[dev]

test36: .venv/py36/bin/py.test ## run tests for Python 3.6
	$(TESTENV) $< -v $(TESTOPTIONS) $(TESTS)

.venv/py37/bin/py.test:
	@conda create -y -m -p .venv/py37 python=3.7
	@# if the conda installation does not work, simply comment out the following line, and let pip handle it
	@conda install -y --override-channels -c defaults -c conda-forge -p .venv/py37 $(CONDA_PACKAGES)
	@.venv/py37/bin/python -m pip install -e .[dev]
	@.venv/py37/bin/python scripts/install-pre-commit.py

test37: .venv/py37/bin/py.test isort-check black-check ## run tests for Python 3.7
	$(TESTENV) $< -v $(TESTOPTIONS) $(TESTS)

$(LATESTVENV)/bin/python: $(LATESTVENV)/bin/py.test


$(LATESTVENV)/bin/sphinx-build: $(LATESTVENV)/bin/py.test


pre-commit-hooks: $(LATESTVENV)/bin/py.test  ## install pre-commit hooks

docs: $(LATESTVENV)/bin/sphinx-build ## generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs MATPLOTLIBRC=../tests SPHINXBUILD=../$(LATESTVENV)/bin/sphinx-build clean
	$(MAKE) -C docs MATPLOTLIBRC=../tests SPHINXBUILD=../$(LATESTVENV)/bin/sphinx-build html
	@echo "open docs/_build/html/index.html"

spellcheck: $(LATESTVENV)/bin/sphinx-build ## check spelling in docs
	@$(LATESTVENV)/bin/pip install sphinxcontrib-spelling
	SPELLCHECK=en_US $(MAKE) -C docs SPHINXBUILD=../$(LATESTVENV)/bin/sphinx-build spelling

black-check: $(LATESTVENV)/bin/python  ## Check all src and test files for complience to "black" code style
	$(LATESTVENV)/bin/black $(BLACKOPTIONS) --diff --check src tests

black: $(LATESTVENV)/bin/python  ## Apply 'black' code style to all src and test files
	$(LATESTVENV)/bin/black $(BLACKOPTIONS) src tests

isort-check: $(LATESTVENV)/bin/python  ## Check all src and test files for correctly sorted imports
	$(LATESTVENV)/bin/isort --recursive --check-only src tests

isort: $(LATESTVENV)/bin/python  ## Sort imports in all src and test files
	$(LATESTVENV)/bin/isort --recursive src tests

coverage: test37  ## generate coverage report in ./htmlcov
	$(LATESTVENV)/bin/coverage html
	@echo "open htmlcov/index.html"

test-upload: $(LATESTVENV)/bin/python clean-build clean-pyc dist ## package and upload a release to test.pypi.org
	$(LATESTVENV)/bin/twine check dist/*
	$(LATESTVENV)/bin/twine upload --repository-url https://test.pypi.org/legacy/ dist/*


upload: $(LATESTVENV)/bin/python clean-build clean-pyc dist ## package and upload a release to pypi.org
	$(LATESTVENV)/bin/twine check dist/*
	$(LATESTVENV)/bin/twine upload dist/*


release: clean $(LATESTVENV)/bin/python ## Create a new version, package and upload it
	$(LATESTVENV)/bin/python ./scripts/release.py


dist: $(LATESTVENV)/bin/python clean-build clean-pyc ## builds source and wheel package
	@$< setup.py sdist
	@$< setup.py bdist_wheel
	ls -l dist

dist-check: $(LATESTVENV)/bin/python  ## Check all dist files for correctness
	$(LATESTVENV)/bin/twine check dist/*

install: clean-build clean-pyc ## install the package to the active Python's site-packages
	pip install .

uninstall:  ## uninstall the package from the active Python's site-packages
	pip uninstall qdyn

develop: clean-build clean-pyc ## install the package to the active Python's site-packages, in develop mode
	pip install -e .[dev]

develop-test: develop ## run tests within the active Python environment
	$(TESTENV) py.test -v $(TESTOPTIONS) $(TESTS)

develop-docs: develop  ## generate Sphinx HTML documentation, including API docs, within the active Python environment
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@echo "open docs/_build/html/index.html"

$(LATESTVENV)/bin/jupyter: $(LATESTVENV)/bin/py.test

# How to execute notebook files
%.ipynb.log: %.ipynb $(LATESTVENV)/bin/jupyter
	@echo ""
	@$(LATESTVENV)/bin/jupyter nbconvert --to notebook --execute --inplace --allow-errors --ExecutePreprocessor.kernel_name='python3' --config=/dev/null $< 2>&1 | tee $@

NOTEBOOKFILES = $(shell find docs/ -maxdepth 1 -iname '*.ipynb')
NOTEBOOKLOGS = $(patsubst %.ipynb,%.ipynb.log,$(NOTEBOOKFILES))

notebooks: $(NOTEBOOKLOGS)  ## re-evaluate the notebooks
	@echo ""
	@echo "All notebook are now up to date; the were executed using the python3 kernel"
	@$(LATESTVENV)/bin/jupyter kernelspec list | grep python3

jupyter-notebook: $(LATESTVENV)/bin/jupyter  ## run a notebook server for editing the examples
	$(LATESTVENV)/bin/jupyter notebook --config=/dev/null

jupyter-lab: $(LATESTVENV)/bin/jupyter  ## run a jupyterlab server for editing the examples
	@$(LATESTVENV)/bin/pip install jupyterlab
	$(LATESTVENV)/bin/jupyter lab --config=/dev/null
