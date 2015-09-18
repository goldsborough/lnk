#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
import ecstasy
import os
import pytest
import requests
import time

from collections import namedtuple

import tests.paths
import lnk.bitly.info

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()

def request_info(url):
	response = requests.get('{0}/info'.format(API),
							params=dict(shortUrl=url,
										access_token=ACCESS_TOKEN))

	return response.json()['data']['info'][0]

def request_history(url):
	response = requests.get('{0}/user/link_history'.format(API),
							params=dict(access_token=ACCESS_TOKEN,
										link=url))

	return response.json()['data']['link_history'][0]

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
		'formatted',
		'template'
		])

	urls = ['http://bit.ly/1V0HZR7', 'http://bit.ly/1V0HPcB']
	expanded = ['http://google.com/', 'http://stackoverflow.com/']
	info = lnk.bitly.info.Info(raw=True)
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
	selection = {}
	# No dictionary comprehension in Python 2.6
	for key, value in data.items():
		if key in sets.values():
			selection[key] = value
	print(selection)
	formatted = ['URL: {0}'.format(urls[0])]
	template = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	for key, value in selection.items():
		if not value:
			formatted.append(info.format(key, 'None'))
		if isinstance(value, list):
			formatted.append('{0}: '.format(key.title()))
			formatted += [template.format(t) for t in value]
		else:
			formatted.append(info.format(key, value))

	return Fixture(info,
					only,
					hide,
					sets,
					urls,
					expanded,
					selection,
					formatted,
					template)

def test_initializes_well(fixture):

	assert hasattr(fixture.info, 'sets')
	assert hasattr(fixture.info, 'reverse')

	reverse = {}
	for key, value in fixture.info.sets.items():
		reverse[value] = key

	assert fixture.info.reverse == reverse

	assert all(i in fixture.info.sets for i in fixture.only)

def test_requests_info_well(fixture):
	expected = request_info(fixture.urls[0])
	result = fixture.info.request_info(fixture.urls[0])

	assert result == expected

def test_requests_history_well(fixture):
	expected = request_history(fixture.urls[0])
	result = fixture.info.request_history(fixture.urls[0])

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
	data = copy.deepcopy(fixture.data)
	del data['tags']
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

	print(result, fixture.formatted)

	assert result[0] == fixture.formatted

def test_fetches_well(fixture):
	result = fixture.info.fetch(fixture.only,
								fixture.hide,
								False,
								fixture.urls)

	data = request_info(fixture.urls[1])
	data.update(request_history(fixture.urls[1]))
	selection = {}
	# No dictionary comprehension in Python 2.6
	for key, value in data.items():
		if key in fixture.sets.values():
			selection[key] = value
	second = ['URL: {0}'.format(fixture.urls[1])]
	for key, value in selection.items():
		second.append(fixture.info.format(key, value))
		if isinstance(value, list):
			second += [fixture.template.format(i) for i in value]
	expected = [fixture.formatted, second]

	result[0].sort()
	result[1].sort()
	expected[0].sort()
	expected[1].sort()

	assert sorted(result) == sorted(expected)
