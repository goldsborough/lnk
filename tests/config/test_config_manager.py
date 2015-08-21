#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json
import pytest
import sys

sys.path.insert(0, os.path.abspath('../..'))

import lnk.config
import lnk.errors

from collections import namedtuple

@pytest.fixture(scope='module')
def fixture(request):
	
	which = 'test'
	filename = '{0}.json'.format(which)

	this = os.path.dirname(os.path.abspath(__file__))
	root = os.path.dirname(os.path.dirname(this))
	path = os.path.join(root, 'config', filename)

	with open(os.path.join(this, filename)) as dummy:
		config = json.load(dummy)
		with open(path, 'w') as test:
			json.dump(config, test)

	def finalize():
		os.remove(path)

	request.addfinalizer(finalize)
	
	Fixture = namedtuple('Fixture', [
		'which',
		'file',
		'manager',
		'config'
		])

	manager = lnk.config.manager.Manager()

	return Fixture(which, path, manager, config)

@pytest.fixture(scope='module')
def changed():

	this = os.path.dirname(os.path.abspath(__file__))

	with open(os.path.join(this, 'changed.json')) as dummy:
		contents = dummy.read()
		config = json.loads(contents)

	Fixture = namedtuple('Fixture', ['contents', 'config'])

	return Fixture(contents, config)


def test_config_manager_opens_correctly(fixture):

	fixture.manager.open(fixture.which)

	assert fixture.manager.file == fixture.file
	assert fixture.manager.config == fixture.config

def test_config_manager_writes_correctly(fixture, changed):
	fixture.manager['fucks'] = -1
	fixture.manager['animal'] = 'unicorn'

	fixture.manager.write()

	with open(fixture.file) as test:
		assert json.load(test) == changed.config

def test_config_manager_throws_for_invalid_key(fixture):
	with pytest.raises(lnk.config.errors.InvalidKeyError):
		fixture.manager['random'] = None

def test_config_manager_context_syntax_works(fixture, changed):

	with lnk.config.manager.Manager(fixture.which) as manager:
		assert manager['fucks'] == -1
		manager['fucks'] = 0
		manager['animal'] = 'cat'
		assert manager.config == fixture.config

	with open(fixture.file) as test:
		assert json.load(test) == fixture.config

def test_config_manager_closes_correctly(fixture):

	fixture.manager.close()

	assert fixture.manager.file is None
	assert fixture.manager.config is None

def test_config_manager_throws_for_write_when_no_file_open(fixture):
	with pytest.raises(lnk.errors.InternalError):
		fixture.manager.write()

def test_config_manager_throws_for_close_when_no_file_open(fixture):
	with pytest.raises(lnk.errors.InternalError):
		fixture.manager.close()
