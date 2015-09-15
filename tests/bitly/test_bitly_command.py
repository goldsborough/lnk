#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import requests

import tests.paths

import bitly.command
import config
import errors

VERSION = 3
API = 'https://api-ssl.bitly.com'
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()

@pytest.fixture(scope='module')

def fixture():
	return bitly.command.Command('link')


def shorten(url='http://python.org', version=VERSION):
	return requests.get('{0}/v{1}/shorten'.format(API, version),
						params=dict(access_token=ACCESS_TOKEN,
									longUrl=url))


def expand(url):
	return requests.get('{0}/v{1}/expand'.format(API, VERSION),
						params=dict(access_token=ACCESS_TOKEN,
									shortUrl=url))


def test_throws_when_not_yet_authenticated():
	with config.Manager('bitly', write=True) as manager:
		old = manager['key']
		manager['key'] = None
	with pytest.raises(errors.AuthorizationError):
		bitly.command.Command('link')
	with config.Manager('bitly', write=True) as manager:
		manager['key'] = old


def test_initializes_well(fixture):
	assert hasattr(fixture, 'parameters')


def test_verify_works_for_healthy_response(fixture):
	response = shorten()
	result = fixture.verify(response, 'even')

	assert result == response.json()['data']


def test_verify_throws_for_http_error(fixture):
	response = shorten(version=123)

	with pytest.raises(errors.HTTPError):
		fixture.verify(response, 'even')

	response = shorten('invalid_uri')

	with pytest.raises(errors.HTTPError):
		fixture.verify(response, 'even')


def test_verify_throws_for_api_error(fixture):
	response = expand('google.com')

	with pytest.raises(errors.APIError):
		fixture.verify(response, 'even', 'expand')


def test_filter_sets_filters_well(fixture):
	base = {i:None for i in 'abcde'}
	only = ['a', 'c', 'e']
	result = bitly.command.filter_sets(base, only, [])

	assert result.keys() == only


def test_filter_sets_hides_well(fixture):
	base = {i:None for i in 'abcde'}
	hide = ['a', 'c', 'e']
	result = bitly.command.filter_sets(base, [], hide)

	assert result.keys() == ['b', 'd']
