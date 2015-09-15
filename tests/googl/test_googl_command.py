#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import requests

import tests.paths

import googl.command
import errors

VERSION = 1
KEY = 'AIzaSyAoXKM_AMBafkXqmVeqJ82o9B9NPCTvXxc'
API = 'https://www.googleapis.com/urlshortener'

@pytest.fixture(scope='module')

def fixture():
	return googl.command.Command('link')


def get(url='http://goo.gl/Euc5', version=VERSION):
	response = requests.get('{0}/v{1}/url'.format(API, version),
						params=dict(shortUrl=url, key=KEY))

	return response

def post(url='http://python.org'):
	headers = {'content-type': 'application/json'}
	data = '{{"longUrl": "{0}"}}'.format(url)
	params = dict(key=KEY)
	response = requests.post('{0}/v{1}/url'.format(API, VERSION),
							 headers=headers,
							 data=data,
							 params=params)
	return response


def test_initializes_well(fixture):
	assert hasattr(fixture, 'parameters')


def test_verify_works_for_healthy_response(fixture):
	response = get()
	result = fixture.verify(response, 'even')

	assert result == response.json()


def test_verify_throws_for_http_error(fixture):
	response = get(version=123)
	with pytest.raises(errors.HTTPError):
		fixture.verify(response, 'even')

	response = get('invalid_uri')
	with pytest.raises(errors.HTTPError):
		fixture.verify(response, 'even')


def test_post_works(fixture):
	response = fixture.post('url', dict(longUrl='http://python.org'))
	expected = post()

	assert response.text == expected.text
