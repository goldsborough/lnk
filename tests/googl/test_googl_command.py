#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apiclient.discovery
import datetime
import httplib2
import oauth2client.file
import os
import pytest
import requests

from collections import namedtuple

import tests.paths

import googl.command
import errors

VERSION = 1
KEY = 'AIzaSyAoXKM_AMBafkXqmVeqJ82o9B9NPCTvXxc'
URL = 'https://www.googleapis.com/urlshortener'
API = apiclient.discovery.build('urlshortener',
								'v{0}'.format(VERSION),
								developerKey=KEY).url()

@pytest.fixture(scope='module')

def fixture():
	Fixture = namedtuple('Fixture', [
		'command',
		'url',
		'credentials_path'
		])

	command = googl.command.Command('link')
	url = 'http://goo.gl/Euc5'
	credentials_path = os.path.join(tests.paths.CONFIG_PATH, 'credentials')

	return Fixture(command,
				   url,
				   credentials_path)


def get(url, projection='FULL'):
	request = API.get(shortUrl=url, projection=projection)
	response = request.execute()

	return response


def test_initializes_well(fixture):
	assert hasattr(fixture.command, 'credentials')


def test_verify_works_for_healthy_response(fixture):
	response = get(fixture.url)
	try:
		fixture.command.verify(response, 'even')
	except errors.HTTPError:
		pytest.fail('googl.command.verify did not'
					'work for a healthy response!')

def test_get_works(fixture):
	pass

def tes_get_api_works(fixture):
	pass

def test_authorize_works(fixture):
	result = fixture.command.authorize()

	assert isinstance(result, httplib2.Http())

def test_authorize_refreshes_well(fixture):
	storage = oauth2client.file.Storage(fixture.credentials_path)
	credentials = storage.get()
	now = datetime.datetime.now()
	credentials.token_expiry = now
	storage.put(credentials)

	fixture.command.authorize()

	credentials = storage.get()

	assert credentials.token_expiry != now


def test_authorize_throws_if_no_credentials(fixture):
	storage = oauth2client.file.Storage(fixture.credentials_path)
	credentials = storage.get()
	os.remove(fixture.credentials_path)

	with pytest.raises(errors.AuthorizationError):
		fixture.command.authorize()

	storage.put(credentials)
