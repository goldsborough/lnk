#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py script for setuptools."""

import re

from setuptools import setup, find_packages

version = ''

def find(thing, where):
	"""Finds __<thing>__ in <where>."""

	pattern = r'^__{0}__\s*=\s*[\'"]([^\'"]*)[\'"]'.format(thing)
	match = re.search(pattern, where, re.MULTILINE)

	return match.group(1)

with open('lnk/__init__.py') as init:
	source = init.read()
	name = find('title', source)
	version = find('version', source)
	author = find('author', source)
	email = find('email', source)
	license_name = find('license', source)
	url = find('url', source)

with open('README.rst') as source:
	readme = source.read()

requirements = [
	'click==4.1',
	'coverage==3.7.1',
	'ecstasy==0.1.3',
	'google-api-python-client==1.4.2',
	'overrides==0.5',
	'pyperclip==1.5.11',
	'requests==2.7.0',
	'ordereddict==1.1',
	'enum34==1.0.4'
]

test_requirements = [
	'pytest==2.7.2',
	'pytest-cache==1.0',
	'python-coveralls==2.5.0',
	'tox==2.1.1'
]

setup(
	name=name,
	version=version,
	description='A command-line URL-shortening client.',
	long_description=readme,
	author=author,
	author_email=email,
	url=url,
	license=license_name,
	classifiers=[
		'Development Status :: 4 - Beta',

		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',

		'Topic :: Internet',
		'Topic :: Desktop Environment',

		'License :: OSI Approved :: MIT License',

		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
	],
	keywords='lnk, url-shortening, bitly, googl, tinyurl',
	include_package_data=True,
	package_data=dict(lnk=[
		'../README.rst',
		'../LICENSE',
		'../Makefile',
		'../config/*',
		'../docs/source/*.rst',
		'../docs/source/conf.py',
		'../docs/Makefile',
		]),
	packages=find_packages(),
	install_requires=requirements,
	test_suite='tests',
	tests_require=test_requirements,
	entry_points=dict(console_scripts=['lnk = lnk.cli:main'])
)
