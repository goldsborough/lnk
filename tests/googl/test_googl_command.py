#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apiclient.discovery
import datetime
import googleapiclient.discovery
import httplib2
import oauth2client.file
import os
import pytest

from collections import namedtuple

import tests.paths

import lnk.googl.command
import lnk.errors

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
		'url'
		])

	lnk.command = lnk.googl.command.Command('link', tests.paths.CREDENTIALS_PATH)
	url = 'http://goo.gl/Euc5'

	return Fixture(lnk.command, url)


def get(url, projection=None):
	request = API.get(shortUrl=url, projection=projection)
	response = request.execute()

	return response


def test_initializes_well(fixture):
	assert hasattr(fixture.command, 'credentials')


def test_get_api_works(fixture):
	result = fixture.command.get_api()

	assert isinstance(result, googleapiclient.discovery.Resource)
	assert all(hasattr(result, i) for i in ['get', 'insert', 'list'])


def test_execute_works_for_healthy_request(fixture):
	request = API.get(shortUrl=fixture.url)
	try:
		response = fixture.command.execute(request)
	except lnk.errors.HTTPError:
		pytest.fail('googl.command.execute threw '
					'an HTTPError for a healthy request!')

	assert isinstance(response, dict)


def test_execute_fails_for_bad_request(fixture):
	request = API.get(shortUrl='banana')

	with pytest.raises(lnk.errors.HTTPError):
		fixture.command.execute(request)


def test_execute_throws_error_with_correct_message(fixture):
	request = API.get(shortUrl='banana')

	with pytest.raises(lnk.errors.HTTPError) as error:
		fixture.command.execute(request, 'badness')

		assert error.value.what == 'badness'


def test_get_works(fixture):
	result = fixture.command.get(fixture.url)
	expected = get(fixture.url)

	assert isinstance(result, dict)
	assert result == expected


def test_authorize_works(fixture):
	result = fixture.command.authorize()

	assert isinstance(result, httplib2.Http)


def test_authorize_refreshes_well():
	storage = oauth2client.file.Storage(tests.paths.CREDENTIALS_PATH)
	credentials = storage.get()
	old = datetime.datetime.now() - datetime.timedelta(days=100)
	credentials.token_expiry = old
	storage.put(credentials)

	command = lnk.googl.command.Command('link', tests.paths.CREDENTIALS_PATH)
	command.authorize()

	credentials = storage.get()

	assert credentials.token_expiry != old


def test_authorize_throws_if_no_credentials(fixture):
	storage = oauth2client.file.Storage(tests.paths.CREDENTIALS_PATH)
	credentials = storage.get()
	os.remove(tests.paths.CREDENTIALS_PATH)

	with pytest.raises(lnk.errors.AuthorizationError):
		fixture.command.authorize()

	storage.put(credentials)
