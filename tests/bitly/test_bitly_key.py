#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import pytest
import re

from collections import namedtuple

import tests.paths
import lnk.bitly.key
import lnk.config
import lnk.errors

@pytest.fixture(scope='module')
def fixture(request):
	Fixture = namedtuple('Fixture', [
		'key',
		'login',
		'password'
		])

	with lnk.config.Manager('bitly', write=True) as config:
		old_key = config['key']
		old_login = config['login']

	def finalize():
		with lnk.config.Manager('bitly', write=True) as config:
				config['key'] = old_key
				config['login'] = old_login

	request.addfinalizer(finalize)

	key = lnk.bitly.key.Key(raw=True)
	login = 'lnktest'
	password = 'ilovecats'

	return Fixture(key, login, password)


def test_key_generation(fixture):
	key = fixture.key.fetch(None,
							fixture.login,
							fixture.password,
							True,
							False)

	assert isinstance(key, str)
	assert len(key) == 40
	assert re.match(r'[a-z\d]', key)

	here = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(here, 'token')
	with open(path, 'wt') as destination:
		destination.write(key)


def test_key_is_hidden_if_show_false(fixture):
	result = fixture.key.fetch(None,
							  fixture.login,
							  fixture.password,
							  False,
							  False)

	assert isinstance(result, str)
	assert result == ''


def test_key_generation_fails_for_bad_login(fixture):
	with pytest.raises(lnk.errors.HTTPError):
		fixture.key.fetch(None, 'bad_login', fixture.password, False, False)


def test_key_generation_fails_for_bad_password(fixture):
	with pytest.raises(lnk.errors.HTTPError):
		fixture.key.fetch(None, fixture.login, 'bad_password', False, False)


def test_who_works_if_someone_is_logged_in(fixture):
	with lnk.config.Manager('bitly', write=True) as config:
		config['login'] = fixture.login
	result = fixture.key.fetch(None, None, None, False, True)
	expected = '{0}\n'.format(fixture.login)

	assert result == expected


def test_who_works_if_nobody_is_logged_in(fixture):
	with lnk.config.Manager('bitly', write=True) as config:
		config['login'] = None
	result = fixture.key.fetch(None, None, None, False, True)
	expected = 'Nobody.\n'

	assert result == expected