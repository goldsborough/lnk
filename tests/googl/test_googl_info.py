#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import oauth2client.file
import pytest
import requests

from collections import namedtuple

import tests.paths
import lnk.googl.info

VERSION = 1
KEY = 'AIzaSyAoXKM_AMBafkXqmVeqJ82o9B9NPCTvXxc'
API = 'https://www.googleapis.com/urlshortener'

def request(url):
	response = requests.get('{0}/v{1}/url'.format(API, VERSION),
							params=dict(projection='FULL',
										shortUrl=url,
										key=KEY))
	return response.json()


@pytest.fixture(scope='module')
def fixture():
	Fixture = namedtuple('Fixture', [
		'info',
		'only',
		'hide',
		'sets',
		'urls',
		'expanded',
		'data',
		'formatted'
		])
	urls = ['http://goo.gl/9RJxHk', 'https://goo.gl/IpUmJn']
	expanded = ['http://python.org/', 'http://github.com/']
	info = lnk.googl.info.Info(raw=True)
	info.credentials = oauth2client.file.Storage(tests.paths.CREDENTIALS_PATH)
	only = ['created', 'expanded']
	hide = ['status']
	sets = {
		"created": "created", 
		"expanded": "longUrl"
	}

	data = request(urls[0])
	selected = {}
	# No dictionary comprehension in Python 2.6
	for key, value in data.items():
		if key in sets.values():
			selected[key] = value
	formatted = ['URL: {0}'.format(urls[0])]
	for key, value in selected.items():
		formatted.append(info.format(key, value))

	return Fixture(info,
					only,
					hide,
					sets,
					urls,
					expanded,
					selected,
					formatted)

def test_initializes_well(fixture):

	assert hasattr(fixture.info, 'sets')
	assert hasattr(fixture.info, 'reverse')

	reverse = dict((v, k) for k, v in fixture.info.sets.items())

	assert fixture.info.reverse == reverse
	assert all(i in fixture.info.sets for i in fixture.only)

def test_requests_well(fixture):
	expected = request(fixture.urls[0])
	result = fixture.info.request(fixture.urls[0])

	assert result == expected

def test_format_sets_keys_well(fixture):
	result = fixture.info.format('status', 'OK')
	expected = 'Status: OK'

	assert result == expected

def test_format_parses_times_well(fixture):
	now = datetime.datetime.now()
	result = fixture.info.format(fixture.sets['created'],
								 now.isoformat())
	expected = 'Created: {0}'.format(now.ctime())

	assert result == expected

def test_lineify_works_without_lists(fixture):
	result = fixture.info.lineify(fixture.urls[0], fixture.data)

	assert result == fixture.formatted

def test_gets_info_well(fixture):
	fixture.info.queue.put(fixture.urls[0])
	result = []
	fixture.info.get_info(fixture.sets.values(), result)

	assert result[0] == fixture.formatted

def test_fetches_well(fixture):
	result = fixture.info.fetch(fixture.only,
								fixture.hide,
								fixture.urls)

	data = request(fixture.urls[1])
	selection = {}
	# No dictionary comprehension in Python 2.6
	for key, value in data.items():
		if key in fixture.sets.values():
			selection[key] = value
	second = ['URL: {0}'.format(fixture.urls[1])]
	second += [fixture.info.format(k, v) for k, v in selection.items()]
	expected = [fixture.formatted, second]

	result[0].sort()
	result[1].sort()
	expected[0].sort()
	expected[1].sort()

	assert sorted(result) == sorted(expected)
