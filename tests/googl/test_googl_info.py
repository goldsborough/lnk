#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import pytest
import requests
import time

from collections import namedtuple

import tests.paths
import googl.link

VERSION = 1
KEY = 'AIzaSyAoXKM_AMBafkXqmVeqJ82o9B9NPCTvXxc'
API = 'https://www.googleapis.com/urlshortener'

def request(url):
	response = requests.get('{0}/{1}/url'.format(API, VERSION),
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
	info = googl.info.Info(raw=True)
	only = ['created', 'expanded', 'user', 'tags']
	hide = ['modified']
	sets = {
		'created': 'created_at', 
        'expanded': 'long_url', 
        'user': 'created_by',
        'tags': 'tags'
	}

	data = request_info(urls[0])
	data.update(request_history(urls[0]))
	selected = {k:v for k, v in data.items() if k in sets.values()}
	formatted = ['URL: {0}'.format(urls[0])]
	for key, value in selected.items():
		if isinstance(value, list):
			formatted.append('{0}: '.format(key.title()))
			formatted += [' + {0}'.format(t) for t in value]
		else:
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

	reverse = {v:k for k, v in fixture.info.sets.items()}

	assert fixture.info.reverse == reverse
	assert all(i in fixture.info.sets for i in fixture.only)
	assert hasattr(fixture.info, 'parameters')
	assert 'projection' in fixture.info.parameters
	assert fixture.info.parameters['projection'] == 'FULL'

def test_requests_well(fixture):
	expected = request(fixture.urls[0])
	result = fixture.info.request_info(fixture.urls[0])

	assert result == expected

def test_format_setss_keys_well(fixture):
	result = fixture.info.format(fixture.sets['user'], 'Borat')
	expected = 'User: Borat'

	assert result == expected

def test_format_parses_times_well(fixture):
	now = time.time()
	result = fixture.info.format(fixture.sets['created'], now)
	expected = 'Created: {0}'.format(time.ctime(now))

	assert result == expected

def test_format_handles_privacy_well(fixture):
	result = fixture.info.format('private', 'Yes')
	expected = 'Private: Yes'

	assert result == expected

def test_format_handles_booleans_well(fixture):
	result = fixture.info.format('private', False)
	expected = 'Private: No'

	assert result == expected

def test_format_handles_None_values_well(fixture):
	result = fixture.info.format(fixture.sets['expanded'], None)
	expected = 'Expanded: None'

	assert result == expected

def test_format_does_not_format_value_if_list(fixture):
	result = fixture.info.format('tags', ['a', 'b', 'c'])
	expected = 'Tags: '

	assert result == expected

def test_lineify_works_without_lists(fixture):
	data = {k:v for k, v in fixture.data.items() if k != 'tags'}
	expected = [fixture.formatted[0]]
	expected += [fixture.info.format(k, v) for k, v in data.items()]
	result = fixture.info.lineify(fixture.urls[0], data, False)

	assert result == expected

def test_lineify_works_with_lists(fixture):
	result = fixture.info.lineify(fixture.urls[0],
								  fixture.data,
								  False)

	assert result == fixture.formatted

def test_lineify_hides_empty_if_wanted(fixture):
	result = fixture.info.lineify(fixture.urls[0],
								  {'Thing': None},
								  True)

	assert result == [fixture.formatted[0]]

def test_requests_well(fixture):
	fixture.info.queue.put(fixture.urls[0])
	result = []
	fixture.info.request(fixture.sets.values(), result, False)

	assert result[0] == fixture.formatted

def test_fetches_well(fixture):
	result = fixture.info.fetch(fixture.only,
								fixture.hide,
								False,
								fixture.urls)

	data = request_info(fixture.urls[1])
	data.update(request_history(fixture.urls[1]))
	data = {k:v for k, v in data.items() if k in fixture.sets.values()}
	second = ['URL: {0}'.format(fixture.urls[1])]
	second += [fixture.info.format(k, v) for k, v in data.items()]
	expected = [fixture.formatted, second]

	result[0].sort()
	result[1].sort()
	result.sort()
	expected[0].sort()
	expected[1].sort()
	expected.sort()

	print(result, expected)

	assert result == expected
