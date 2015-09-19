#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
import ecstasy
import oauth2client.file
import pytest
import requests

from collections import namedtuple

import tests.paths
import lnk.googl.stats
import lnk.googl.info
import lnk.config

VERSION = 1
API = 'https://www.googleapis.com/urlshortener'
KEY = 'AIzaSyAoXKM_AMBafkXqmVeqJ82o9B9NPCTvXxc'

def request_stats(url):
	response = requests.get('{0}/v{1}/url'.format(API, VERSION),
							params=dict(projection='FULL',
										shortUrl=url,
										key=KEY))
	data = response.json()
	data['URL'] = url
	del data['kind']
	del data['id']

	return data

@pytest.fixture(scope='module')
def fixture(request):
	Fixture = namedtuple('Fixture', [
		'stats',
		'info',
		'category',
		'url',
		'timespans',
		'full',
		'analytics',
		'first_level',
		'second_level',
		'forever_data',
		'category_data',
		'timespans_data'
		])

	category = {'browsers': 'browsers'}
	url = 'http://goo.gl/3U9mIa'
	timespans = ['month', 'day']
	first_level = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	second_level = ecstasy.beautify('   <-> {0}: {1}', ecstasy.Color.Yellow)
	full = request_stats(url)
	analytics = full['analytics']
	forever_data = analytics['allTime']
	category_data = forever_data['browsers']
	timespans = ['month', 'week']
	timespans_data = [analytics[i] for i in timespans]

	with lnk.config.Manager('googl', write=True) as manager:
		settings = manager['commands']['stats']['settings']
		old = settings['timespan']

	stats = lnk.googl.stats.Stats(raw=True)
	stats.credentials = oauth2client.file.Storage(tests.paths.CREDENTIALS_PATH)
	info = lnk.googl.info.Info(raw=True)
	info.credentials = oauth2client.file.Storage(tests.paths.CREDENTIALS_PATH)

	def finalize():
		with lnk.config.Manager('googl', write=True) as manager:
			settings = manager['commands']['stats']['settings']
			settings['span'] = old

	request.addfinalizer(finalize)

	return Fixture(stats,
				   info,
				   category,
				   url,
				   timespans,
				   full,
				   analytics,
				   first_level,
				   second_level,
				   forever_data,
				   category_data,
				   timespans_data)


def test_format_makes_lines_pretty(fixture):
	result = fixture.stats.format('foo', 'bar')
	expected = 'Foo: bar'

	assert result == expected


def test_format_handles_special_keys_wells(fixture):
	result = fixture.stats.format('shortUrlClicks', 'foo')
	expected = 'Clicks: foo'

	assert result == expected

	result = fixture.stats.format('longUrl', 'foo')
	expected = 'Expanded: foo'

	assert result == expected


def test_get_timespans_removes_duplicates(fixture):
	things = [1, 4, 2, 3, 4, 1, 3, 3]
	result = fixture.stats.get_timespans(things, False)
	expected = set(things)

	assert result == expected


def test_get_timespans_picks_default_timespan_if_no_times():
	with lnk.config.Manager('googl', write=True) as manager:
		settings = manager['commands']['stats']['settings']
		settings['timespan'] = 'day'
	stats = lnk.googl.stats.Stats(raw=True)
	result = stats.get_timespans([], False)

	assert result == set(['day'])

def test_get_timespans_handles_default_forever_well():
	with lnk.config.Manager('googl', write=True) as manager:
		settings = manager['commands']['stats']['settings']
		settings['timespan'] = 'forever'
	stats = lnk.googl.stats.Stats(raw=True)
	result = stats.get_timespans([], False)

	assert result == set(['allTime'])


def test_get_timespans_handles_default_two_hours_well():
	with lnk.config.Manager('googl', write=True) as manager:
		settings = manager['commands']['stats']['settings']
		settings['timespan'] = 'two-hours'
	stats = lnk.googl.stats.Stats(raw=True)
	result = stats.get_timespans([], False)

	assert result == set(['twoHours'])

def test_get_timespans_handles_forever_well(fixture):
	result = fixture.stats.get_timespans([], True)

	assert result == set(['allTime'])


def test_get_timespans_handles_two_hours_well(fixture):
	result = fixture.stats.get_timespans(['two-hours'], False)

	assert result == set(['twoHours'])


def test_get_timespans_works(fixture):
	result = fixture.stats.get_timespans(fixture.timespans, False)

	assert result == set(fixture.timespans)


def test_sub_listify_works_in_normal_cases(fixture):
	result = fixture.stats.sub_listify(fixture.category,
										 fixture.category_data,
										 None,
										 False)
	expected = []
	for point in fixture.category_data:
		line = fixture.second_level.format(point['id'], point['count'])
		expected.append(line)

	assert result == expected


def test_sub_listify_limits_well(fixture):
	result = fixture.stats.sub_listify(fixture.category,
										fixture.category_data,
										1,
										False)
	expected = [fixture.second_level.format(fixture.category_data[0]['id'],
											fixture.category_data[0]['count'])]
	assert len(result) == 1
	assert result == expected


def test_sub_listify_handles_unknown_well(fixture):
	data = [dict(id='unknown', count=123)]
	result = fixture.stats.sub_listify(fixture.category,
									   data,
									   None,
									   False)
	expected = [fixture.second_level.format('Unknown', 123)]

	assert result == expected


def test_sub_listify_leaves_countries_short(fixture):
	data = [dict(id='DE', count=123)]
	result = fixture.stats.sub_listify('countries',
									   data,
									   None,
									   False)
	expected = [fixture.second_level.format('DE', 123)]

	assert result == expected

def test_sub_listify_expands_countries(fixture):
	data = [dict(id='DE', count=123)]
	result = fixture.stats.sub_listify('countries',
									   data,
									   None,
									   True)
	expected = [fixture.second_level.format('Germany', 123)]

	assert result == expected


def test_get_header_handles_forever_well(fixture):
	result = fixture.stats.get_header('allTime')
	expected = fixture.first_level.format('Since forever:')

	assert result == expected


def test_get_header_handles_two_hours_well(fixture):
	result = fixture.stats.get_header('twoHours')
	expected = fixture.first_level.format('Last two hours:')

	assert result == expected


def test_get_header_handles_normal_cases_well(fixture):
	result = fixture.stats.get_header('month')
	expected = fixture.first_level.format('Last month:')

	assert result == expected


def test_request_format_is_correct(fixture):
	fixture.stats.queue.put(fixture.url)
	result = fixture.stats.request(False)

	assert isinstance(result, dict)
	assert 'URL' in result
	assert (isinstance(result['URL'], str)
		 or isinstance(result['URL'], unicode))
	assert 'analytics' in result
	assert isinstance(result['analytics'], dict)


def test_requests_well_with_info(fixture):
	fixture.stats.queue.put(fixture.url)
	result = fixture.stats.request(True)

	assert result == fixture.full


def test_requests_well_without_info(fixture):
	fixture.stats.queue.put(fixture.url)
	result = fixture.stats.request(False)
	expected = fixture.full.copy()
	for i in ['status', 'created', 'longUrl']:
		del expected[i]

	assert result == expected


def test_listify_formats_timespans_well(fixture):
	timespans = ['allTime'] + fixture.timespans
	result = fixture.stats.listify(fixture.analytics,
								   fixture.category,
								   timespans,
								   False,
								   None)

	expected = [fixture.first_level.format('Since forever:')]
	for i in fixture.timespans:
		header = fixture.first_level.format('Last {0}:'.format(i))
		expected.append(header)

	for i in expected:
		assert i in result


def test_listify_filters_timespans_well(fixture):
	result = fixture.stats.listify(fixture.analytics,
								   fixture.category,
								   fixture.timespans,
								   False,
								   None)
	for i in fixture.timespans:
		line = 'Last {0}:'.format(i)
		formatted = fixture.first_level.format(line)
		assert formatted in result

	unwanted = ['Since forever', 'Last day:', 'Last two hours:']
	for i in unwanted:
		formatted = fixture.first_level.format(i)
		assert formatted not in result


def test_listify_handles_clicks_well(fixture):
	result = fixture.stats.listify(fixture.analytics,
								   {'clicks': 'shortUrlClicks'},
								   [fixture.timespans[0]],
								   False,
								   None)
	clicks = fixture.analytics[fixture.timespans[0]]['shortUrlClicks']
	line = 'Last {0}: {1}'.format(fixture.timespans[0], clicks)
	expected = fixture.first_level.format(line)

	assert expected in result


def test_lineify_formats_headers_well(fixture):
	data = copy.deepcopy(fixture.full)
	result = fixture.stats.lineify(data,
								   fixture.category,
								   fixture.timespans,
								   False,
								   None)
	for key, value in fixture.full.items():
		if key != 'analytics':
			expected = fixture.stats.format(key, value)
			assert expected in result

def test_get_stats_works(fixture):
	"""
	result = []
	fixture.stats.get_stats(result,
							fixture.category,
							fixture.timespans,
							True,
							False,
							None)
	assert result[0] == fixture.full
	"""
	pass


def test_fetch_works_for_single_url(fixture):
	result = fixture.stats.fetch(fixture.category.keys(),
								 [],
								 fixture.timespans,
								 False,
								 None,
								 True,
								 False,
								 [fixture.url])
	data = copy.deepcopy(fixture.full)
	expected = fixture.stats.lineify(data,
									 fixture.category,
									 fixture.timespans,
									 False,
									 None)

	assert sorted(result[0]) == sorted(expected)


def test_fetch_limits_well(fixture):
	result = fixture.stats.fetch(fixture.category.keys(),
								 [],
								 fixture.timespans,
								 False,
								 1,
								 True,
								 False,
								 [fixture.url])
	data = copy.deepcopy(fixture.full)
	expected = fixture.stats.lineify(data,
									 fixture.category,
									 fixture.timespans,
									 False,
									 1)

	assert sorted(result[0]) == sorted(expected)

def test_fetch_works_for_many_urls(fixture):
	other = 'http://goo.gl/XBzv0g'
	result = fixture.stats.fetch(fixture.category.keys(),
								 [],
								 fixture.timespans,
								 False,
								 None,
								 True,
								 False,
								 [fixture.url, other])
	result = sorted(sorted(i) for i in result)
	data = copy.deepcopy(fixture.full)
	expected = []
	first = fixture.stats.lineify(data,
			  					   fixture.category,
								   fixture.timespans,
								   False,
								   None)
	expected.append(sorted(first))
	other_data = request_stats(other)
	second = fixture.stats.lineify(other_data,
			  					   fixture.category,
								   fixture.timespans,
								   False,
								   None)
	expected.append(sorted(second))

	assert result == sorted(expected)


def test_fetch_adds_info_well(fixture):
	result = fixture.stats.fetch(fixture.category.keys(),
								 [],
								 fixture.timespans,
								 False,
								 1,
								 True,
								 False,
								 [fixture.url])
	data = copy.deepcopy(fixture.full)
	expected = fixture.stats.lineify(data,
									 fixture.category,
									 fixture.timespans,
									 False,
									 1)

	assert sorted(result[0]) == sorted(expected)
