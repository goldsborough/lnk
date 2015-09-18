.PHONY: clean-pyc clean-build docs clean
 
help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "test-register - register the project at TestPyPI"
	@echo "register - register the project at PyPI"
	@echo "test-release - package and upload a releaes to TestPyPI"
	@echo "release - package and upload a release to PyPI"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
 
clean: clean-build clean-pyc clean-test
 
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
 
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
 
clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
 
lint:
	pylint ecstasy
 
test:
	python setup.py test
 
coverage:
	coverage run -m pytest
	coverage report -m
	coverage html
	open htmlcov/index.html
 
docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/build/html/index.html

test-register:
	python setup.py register -r test

register:
	python setup.py register

test-release: clean
	twine upload -r test sdist
	twine upload -r test bdist_wheel

release: clean
	twine upload dist/*
 
dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
 
install: clean
	python setup.py install