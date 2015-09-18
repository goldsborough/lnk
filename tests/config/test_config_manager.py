#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json
import pytest

from collections import namedtuple

import tests.paths

import lnk.config
import lnk.errors

HERE = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope='module')
def fixture(request):
	Fixture = namedtuple('Fixture', [
		'which',
		'file',
		'manager',
		'config'
		])

	which = 'test_manager'
	filename = '{0}.json'.format(which)
	path = os.path.join(tests.paths.CONFIG_PATH, filename)

	with open(os.path.join(HERE, filename)) as source:
		config = json.load(source)
		with open(path, 'w') as test:
			json.dump(config, test)

	def finalize():
		os.remove(path)

	request.addfinalizer(finalize)

	manager = lnk.config.Manager()

	return Fixture(which, path, manager, config)

@pytest.fixture(scope='module')
def changed():
	Fixture = namedtuple('Fixture', ['contents', 'config'])
	with open(os.path.join(HERE, 'changed_manager.json')) as source:
		contents = source.read()
		config = json.loads(contents)

	return Fixture(contents, config)



def test_opens_correctly(fixture):
	fixture.manager.open(fixture.which)

	assert fixture.manager.file == fixture.file
	assert fixture.manager.config == fixture.config


def test_writes_correctly(fixture, changed):
	fixture.manager['fucks'] = -1
	fixture.manager['animal'] = 'unicorn'

	fixture.manager.write()

	with open(fixture.file) as test:
		assert json.load(test) == changed.config


def test_throws_for_invalid_key(fixture):
	with pytest.raises(lnk.errors.InvalidKeyError):
		fixture.manager['random'] = None


def test_context_syntax_closes_well(fixture):
	with lnk.config.Manager(fixture.which) as manager:
		assert manager['fucks'] == -1
		assert manager['animal'] == 'unicorn'
		manager['fucks'] = 0
		manager['animal'] = 'cat'
		assert manager.config == fixture.config
		manager.write()

	with open(fixture.file) as test:
		assert json.load(test) == fixture.config


def test_context_syntax_writes_well(fixture, changed):
	with lnk.config.Manager(fixture.which, write=True) as manager:
		assert manager['fucks'] == 0
		assert manager['animal'] == 'cat'
		manager['fucks'] = -1
		manager['animal'] = 'unicorn'
		assert manager.config == changed.config

	with open(fixture.file) as test:
		assert json.load(test) == changed.config


def test_properties_are_accessible(fixture, changed):
	print(fixture, changed)
	print(fixture.manager.config, changed.config)
	assert sorted(fixture.manager.keys) == sorted(changed.config.keys())
	assert sorted(fixture.manager.values) == sorted(changed.config.values())
	assert sorted(fixture.manager.items) == sorted(changed.config.items())


def test_get_works(changed):
	result = lnk.config.get('test_manager', 'animal')
	expected = changed.config['animal']

	assert result == expected


def test_closes_correctly(fixture):
	fixture.manager.close()

	assert fixture.manager.file is None
	assert fixture.manager.config is None


def test_throws_for_write_when_no_file_open(fixture):
	with pytest.raises(lnk.errors.InternalError):
		fixture.manager.write()


def test_throws_for_close_when_no_file_open(fixture):
	with pytest.raises(lnk.errors.InternalError):
		fixture.manager.close()
