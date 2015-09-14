#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import requests

import bitly.command
import config
import errors
import tests.paths

with open('token') as source:
	ACCESS_TOKEN = source.read()

@pytest.fixture(scope='module')
def fixture():
	return bitly.command.Command('link')

def request(url='http://python.org', version=3):
	api = 'https://api-ssl.bitly.com/v{0}/shorten'
	return requests.get(api.format(version),
						params=dict(access_token=ACCESS_TOKEN,
									longUrl=url))

def test_bitly_command_throws_when_not_yet_authenticated():
	with config.Manager('bitly') as manager:
		manager['key'] = None
		with pytest.raises(errors.AuthorizationError):
			bitly.command.Command('link')

def test_bitly_command_initializes_well(fixture):
	assert hasattr(fixture, 'parameters')

def test_bitly_command_verify_works_for_healthy_response(fixture):
	response = request()
	result = fixture.verify(response, 'even')

	assert result == response.json()

def test_bitly_command_verify_throws_for_http_error(fixture):
	response = request(version=123)
	with pytest.raises(errors.HTTPError):
		fixture.verify(response, 'even')

def test_bitly_command_verify_throws_for_api_error(fixture):
	response = request('invalid_url')
	with pytest.raises(errors.APIError):
		fixture.verify(response, 'even')