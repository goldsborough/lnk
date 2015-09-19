#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py script for setuptools."""

import json
import os.path
import re

import setuptools
import setuptools.command.install

with open(os.path.join('lnk', '__init__.py')) as init:
	INIT = init.read()


def get(thing):
	"""Retrieves a setup value."""
	if thing == 'readme':
		with open('README.rst') as readme:
			return readme.read()
	pattern = r'^__{0}__\s*=\s*[\'"]([^\'"]*)[\'"]'.format(thing)
	match = re.search(pattern, INIT, re.MULTILINE)

	return match.group(1)


class Install(setuptools.command.install.install):
	"""Subclass of setuptool's install class to have a post-install task."""

	def run(self):
		setuptools.command.install.install.run(self)
		self.execute(self.reset, [], msg='Running post-install task...')

	@staticmethod
	def reset():
		"""Resets any old authorization keys for a new user."""
		for_bitly = os.path.join('config', 'bitly.json')
		with open(for_bitly) as source:
			config = json.load(source)
		config['key'] = None
		with open(for_bitly, 'w') as destination:
			json.dump(config, destination, indent=4)
		for_googl = os.path.join('config', '.credentials')
		if os.path.exists(for_googl):
			os.remove(for_googl)


setuptools.setup(
	cmdclass=dict(install=Install),
	name=get('title'),
	version=get('version'),
	description='A command-line URL-shortening client.',
	long_description=get('readme'),
	author=get('author'),
	author_email=get('email'),
	url=get('url'),
	license=get('license'),
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
	packages=setuptools.find_packages(exclude=['scripts']),
	install_requires=[
		'click==4.1',
		'coverage==3.7.1',
		'ecstasy==0.1.3',
		'google-api-python-client==1.4.2',
		'pyperclip==1.5.11',
		'requests==2.7.0',
		'ordereddict==1.1',
		'enum34==1.0.4'
	],
	test_suite='tests',
	tests_require=[
		'pytest==2.7.2',
		'pytest-cache==1.0',
		'python-coveralls==2.5.0',
		'tox==2.1.1'
	],
	entry_points=dict(console_scripts=['lnk = lnk.cli:main'])
)
