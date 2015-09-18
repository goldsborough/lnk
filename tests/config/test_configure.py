#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json
import pytest

from collections import namedtuple

import tests.paths
import lnk.errors

from lnk.config import configure

@pytest.fixture(scope='module')
def fixture(request):
	Fixture = namedtuple('Fixture', [
		'service',
		'command',
		'path',
		'original',
		'changed',
		'keys',
		'old_values',
		'new_values'
		])
	service = 'test_command'
	lnk.command = 'cmd'

	here = os.path.dirname(os.path.abspath(__file__))
	original_file = '{0}.json'.format(service)
	path = os.path.join(tests.paths.CONFIG_PATH, original_file)
	with open(os.path.join(here, original_file)) as source:
		original = json.load(source)
		with open(path, 'w') as test:
			json.dump(original, test)

	changed_file = '{0}.json'.format('changed_command')
	with open(os.path.join(here, changed_file)) as source:
			changed = json.load(source)

	keys = ['rock', 'water']
	old_values = ['solid', 'liquid']
	new_values = ['gas', 'solid']

	def finalize():
		os.remove(path)

	request.addfinalizer(finalize)

	return Fixture(service,
				   lnk.command,
				   path,
				   original,
				   changed,
				   keys,
				   old_values,
				   new_values)

def test_configure_can_be_quiet(fixture):
	result = configure.configure(fixture.service,
								None,
								fixture.keys,
								fixture.old_values,
								True,
								False)
	assert result is None


def test_configure_updates_well(fixture):
	configure.configure(fixture.service,
						None,
						fixture.keys,
						fixture.new_values,
						True,
						False)

	with open(fixture.path) as source:
		result = json.load(source)

	assert result == fixture.changed


def test_configure_returns_correct_output(fixture):
	result = configure.configure(fixture.service,
								 None,
								 fixture.keys,
								 fixture.old_values,
								 False,
								 False)
	lines = []
	# Note that we updated back to the old values
	# (that's why the name switch)
	items = zip(fixture.keys, fixture.new_values, fixture.old_values)
	for key, old, new in items:
		line = '{0}: {1} => {2}'.format(key, old, new)
		lines.append(line)
	expected = '{0}\n'.format('\n'.join(lines))

	assert result == expected


def test_configure_updates_command_settings_well(fixture):
	configure.configure(fixture.service,
						fixture.command,
						['foo', 'bar'],
						[False, 123],
						True,
						False)
	with open(fixture.path) as source:
		result = json.load(source)

	expected = fixture.original
	settings = expected['commands']['cmd']['settings']
	settings['foo'] = False
	settings['bar'] = 123

	assert result == expected


def test_format_value_formats_integers():
	result = configure.format_value(5)

	assert result == '5'


def test_format_value_formats_lists():
	items = [1, 2, 3, 4]
	result = configure.format_value(items)
	expected = ', '.join(map(str, items))

	assert result == expected


def test_format_value_formats_dictionaries():
	items = {'foo': 1, 'bar': True, 'cats': 'please'}
	result = configure.format_value(items)
	expected = ', '.join('{0}: {1}'.format(k, v) for k, v in items.items())

	assert result == expected


def test_update_formats_well_if_no_value_given():
	result = configure.update({'foo': 0}, 'foo', None)
	expected = 'foo: 0'

	assert result == expected


def test_update_formats_well_if_value_given():
	result = configure.update({'foo': 0}, 'foo', [1])
	expected = 'foo: 0 => 1'

	assert result == expected


def test_update_updates_well():
	settings = {'foo': 0}
	configure.update(settings, 'foo', [1])
	
	assert settings['foo'] == 1
