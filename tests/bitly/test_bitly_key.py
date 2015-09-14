#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import re

import tests.paths
import bitly.key
import config
import errors

LOGIN = 'lnktest'
PASSWORD = 'ilovecats'

@pytest.fixture(scope='module')
def fixture(request):
	with config.Manager('bitly') as manager:
		old = manager['key']
	def finalize():
		with config.Manager('bitly', write=True) as manager:
				manager['key'] = old
	request.addfinalizer(finalize)
	return bitly.key.Key(raw=True)

def test_bitly_key_generation(fixture):
	key = fixture.fetch(None, LOGIN, PASSWORD, True)

	assert isinstance(key, str)
	assert len(key) == 40
	assert re.match(r'[a-z\d]', key)

	with open('token', 'wt') as destination:
		destination.write(key)

def test_bitly_key_is_hidden_if_show_false(fixture):
	result = fixture.fetch(None, LOGIN, PASSWORD, False)

	assert isinstance(result, str)
	assert result == ''

def test_bitly_key_generation_fails_for_bad_login(fixture):
	with pytest.raises(errors.HTTPError):
		fixture.fetch(None, 'bad_login', PASSWORD, False)

def test_bitly_key_generation_fails_for_bad_password(fixture):
	with pytest.raises(errors.HTTPError):
		fixture.fetch(None, LOGIN, 'bad_password', False)

