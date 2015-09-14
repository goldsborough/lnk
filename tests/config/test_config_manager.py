#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json
import pytest

from collections import namedtuple

import tests.path

import config
import errors


HERE = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope='module')
def fixture(request):
	which = 'test'
	filename = '{0}.json'.format(which)
	path = os.path.join(tests.path.CONFIG_PATH, filename)

	with open(os.path.join(HERE, filename)) as dummy:
		configuration = json.load(dummy)
		with open(path, 'w') as test:
			json.dump(configuration, test)

	def finalize():
		os.remove(path)

	request.addfinalizer(finalize)
	
	Fixture = namedtuple('Fixture', [
		'which',
		'file',
		'manager',
		'config'
		])

	manager = config.Manager()

	return Fixture(which, path, manager, configuration)

@pytest.fixture(scope='module')
def changed():
	with open(os.path.join(HERE, 'changed.json')) as dummy:
		contents = dummy.read()
		configuration = json.loads(contents)

	Fixture = namedtuple('Fixture', ['contents', 'config'])

	return Fixture(contents, configuration)


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
	with pytest.raises(errors.InvalidKeyError):
		fixture.manager['random'] = None

def test_config_manager_context_syntax_closes_well(fixture):
	with config.Manager(fixture.which) as manager:
		assert manager['fucks'] == -1
		assert manager['animal'] == 'unicorn'
		manager['fucks'] = 0
		manager['animal'] = 'cat'
		assert manager.config == fixture.config
		manager.write()

	with open(fixture.file) as test:
		assert json.load(test) == fixture.config

def test_config_manager_context_syntax_writes_well(fixture, changed):
	with config.Manager(fixture.which, write=True) as manager:
		assert manager['fucks'] == 0
		assert manager['animal'] == 'cat'
		manager['fucks'] = -1
		manager['animal'] = 'unicorn'
		assert manager.config == changed.config

	with open(fixture.file) as test:
		assert json.load(test) == changed.config

def test_config_manager_properties_are_accessible(fixture, changed):
	assert fixture.manager.keys == changed.config.keys()
	assert fixture.manager.values == changed.config.values()
	assert fixture.manager.items == changed.config.items()

def test_config_get_function_works(changed):
	assert config.get('test', 'animal') == changed.config['animal']

def test_config_manager_closes_correctly(fixture):
	fixture.manager.close()

	assert fixture.manager.file is None
	assert fixture.manager.config is None

def test_config_manager_throws_for_write_when_no_file_open(fixture):
	with pytest.raises(errors.InternalError):
		fixture.manager.write()

def test_config_manager_throws_for_close_when_no_file_open(fixture):
	with pytest.raises(errors.InternalError):
		fixture.manager.close()
