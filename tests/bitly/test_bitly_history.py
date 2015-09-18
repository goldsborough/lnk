#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ecstasy
import os
import pytest
import requests
import time

from collections import namedtuple

import tests.paths
import lnk.bitly.history

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()


def timestamp(time_range):
	seconds = {
		"minute": 60, 
		"hour": 3600, 
		"day": 86400,
		"week": 604800, 
		"month": 2629740,
		"year": 31556900
	}
	offset = time_range[0] * seconds[time_range[1]]

	return int(time.time() - offset)

def request_history(start=None, end=None, limit=None):
	if start:
		start = timestamp(start)
	if end:
		end = timestamp(end)
	response = requests.get('{0}/user/link_history'.format(API),
							params=dict(access_token=ACCESS_TOKEN,
										created_after=start,
										created_before=end,
										limit=limit))
	data = response.json()['data']

	return [i['link'] for i in data['link_history']]


def request_expansion(url):
	response = requests.get('{0}/expand'.format(API),
							params=dict(access_token=ACCESS_TOKEN,
										shortUrl=url))
	data = response.json()['data']

	return data['expand'][0]['long_url']


@pytest.fixture(scope='module')
def fixture():
	
	Fixture = namedtuple('Fixture', [
		'history',
		'forever_data',
		'last',
		'last_data',
		'ranges',
		'ranges_data',
		'template',
		'url',
		'expanded'
		])

	history = lnk.bitly.history.History(raw=True)
	forever_data = request_history()

	last = [(4, 'week'), (5, 'month')]
	last_data = [request_history(i) for i in last]

	ranges = [(5, 'month', 4, 'day'), (7, 'year', 1, 'day')]
	ranges_data = [request_history(i[:2], i[2:]) for i in ranges]

	template = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	url = 'http://bit.ly/1OQM9nA'
	expanded = request_expansion(url)

	return Fixture(history,
				   forever_data,
				   last,
				   last_data,
				   ranges,
				   ranges_data,
				   template,
				   url,
				   expanded)


def test_initializes_well(fixture):
	assert hasattr(fixture.history, 'raw')
	assert hasattr(fixture.history, 'link')
	assert hasattr(fixture.history, 'seconds')
	assert isinstance(fixture.history.seconds, dict)

def test_request_works(fixture):
	expected = request_history()
	result = fixture.history.request()

	print(result, expected)

	assert sorted(result) == sorted(expected)


def test_lineify_does_nothing_if_pretty_false(fixture):
	result = fixture.history.lineify('cat', False, False, False)

	assert result == 'cat'


def test_lineify_prettifies_if_pretty_true(fixture):
	result = fixture.history.lineify('cat', False, False, True)
	expected = fixture.template.format('cat')

	assert result == expected


def test_lineify_returns_only_expanded_if_expanded_true(fixture):
	result = fixture.history.lineify(fixture.url, True, False, False)

	assert result == fixture.expanded


def test_lineify_returns_both_if_both_true(fixture):
	result = fixture.history.lineify(fixture.url, False, True, False)
	expected = '{0} => {1}'.format(fixture.url, fixture.expanded)

	assert result == expected


def test_timestamp_works(fixture):
	now = time.time()
	result = fixture.history.timestamp((1, 'minute'), now)
	expected = int(now - 60)

	assert result == expected


def test_timestamp_works_if_endswith_s(fixture):
	now = time.time()
	result = fixture.history.timestamp((1, 'minutes'), now)
	expected = int(now - 60)

	assert result == expected	


def test_parse_time_works_without_upper_bound(fixture):
	now = time.time()
	result = fixture.history.parse_time((1, 'minute'), base=now)
	expected = int(now - 60)

	assert result['created_after'] == expected
	assert result['created_before'] is None


def test_parse_time_works_with_upper_bound(fixture):
	now = int(time.time())
	result = fixture.history.parse_time((2, 'minute'), (1, 'minute'), now)

	assert result['created_after'] == now - 120
	assert result['created_before'] == now - 60


def test_last_works_for_single_range(fixture):
	result = fixture.history.last([fixture.last[0]], False, False, False)
	expected = fixture.last_data[0]

	assert result == expected

def test_last_works_for_many_ranges(fixture):
	result = fixture.history.last(fixture.last, False, False, False)
	expected = fixture.last_data[0] + fixture.last_data[1]

	assert result == expected

def test_ranges_works_for_single_range(fixture):
	result = fixture.history.ranges([fixture.ranges[0]], False, False, False)
	expected = fixture.ranges_data[0]

	assert result == expected


def test_ranges_works_for_many_ranges(fixture):
	result = fixture.history.ranges(fixture.ranges, False, False, False)
	expected = [j for i in fixture.ranges_data for j in i]

	assert sorted(result) == sorted(expected)


def test_forever_works(fixture):
	result = fixture.history.forever(False, False, False)
	expected = fixture.forever_data

	assert result == expected


def test_pretty_works_for_forever(fixture):
	result = fixture.history.forever(False, False, True)
	expected = ['Since forever:']
	expected += [fixture.template.format(i) for i in fixture.forever_data]

	assert result == expected + ['']

def test_pretty_works_for_last(fixture):
	result = fixture.history.last(fixture.last, False, False, True)
	expected = []
	for time_point, data in zip(fixture.last, fixture.last_data):
		header = 'Last {0} {1}:'.format(time_point[0], time_point[1])
		if not data:
			header += ' None'
		expected.append(header)
		for item in data:
			expected.append(fixture.template.format(item))
		expected.append('')

	assert sorted(result) == sorted(expected)

def test_ranges_header_removes_unit_if_both_equal(fixture):
	after = (7, 'days')
	before = (2, 'days')
	result = fixture.history.ranges_header(after, before, True)
	expected = 'Between 7 and 2 days ago:'

	assert result == expected

def test_pretty_works_for_ranges(fixture):
	result = fixture.history.ranges(fixture.ranges, False, False, True)
	expected = []
	for time_point, data in zip(fixture.ranges, fixture.ranges_data):
		header = 'Between {0} {1} '.format(time_point[0], time_point[1])
		header += 'and {0} {1} ago:'.format(time_point[2], time_point[3])
		if not data:
			header += ' None'
		expected.append(header)
		for item in data:
			expected.append(fixture.template.format(item))
		expected.append('')

	assert sorted(result) == sorted(expected)


def test_fetch_works_only_for_forever(fixture):
	result = fixture.history.fetch(None, None, True, None, False, False, False)
	expected = fixture.forever_data

	assert result == expected


def test_fetch_removes_last_line(fixture):
	result = fixture.history.fetch(None, None, True, None, False, False, True)
	expected = len(['Since forever:'] + fixture.forever_data)

	assert len(result) == expected
	assert result[-1] != ''


def test_fetch_works_for_all_ranges(fixture):
	result = fixture.history.fetch(fixture.last,
								   fixture.ranges,
								   True,
								   None,
								   False,
								   False,
								   False)
	expected = [fixture.forever_data] + fixture.last_data + fixture.ranges_data
	expected = [j for i in expected for j in i]

	assert sorted(result) == sorted(expected)


def test_fetch_limits_well(fixture):
	result = fixture.history.fetch(None, None, True, 3, False, False, False)
	expected = fixture.forever_data[:3]

	assert len(result) <= 3
	assert result == expected
