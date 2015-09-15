#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import requests

import tests.paths

import errors
import tinyurl.command

@pytest.fixture(scope='module')
def fixture():
	return tinyurl.command.Command('link')

def request(url='http://python.org', response_format='json', version=1):
	return requests.get('http://tiny-url.info/api/v{0}/create'.format(version),
						params=dict(apikey='0BFA4A7B5BDD5BE7780C',
									 format=response_format,
									 provider='tinyurl_com',
									 url=url))

def test_verify_works_for_healthy_response(fixture):
	response = request()
	data = fixture.verify(response, 'even')

	assert data == response.json()

def test_verify_throws_for_http_error(fixture):
	response = request(version=123)
	with pytest.raises(errors.HTTPError):
		fixture.verify(response, 'even')

def test_verify_throws_for_api_error(fixture):
	response = request('telegram')
	with pytest.raises(errors.APIError):
		fixture.verify(response, 'even')

