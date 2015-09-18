#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
import ecstasy
import os
import pytest
import requests

from collections import namedtuple

import tests.paths
import lnk.bitly.stats
import lnk.bitly.info
import lnk.config

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()

def request_stats(url, endpoint, timespan):
	response = requests.get('{0}/link/{1}'.format(API, endpoint),
							params=dict(units=timespan.span,
										unit=timespan.unit,
										access_token=ACCESS_TOKEN,
										link=url))

	e = endpoint if endpoint != 'clicks' else 'link_clicks'
	data = response.json()['data'][e]

	return {'timespan': timespan, 'data': data}

@pytest.fixture(scope='module')
def fixture(request):
	Fixture = namedtuple('Fixture', [
		'stats',
		'info',
		'endpoint',
		'url',
		'timespan_tuples',
		'timespans',
		'forever',
		'first_level',
		'second_level',
		'forever_data',
		'timespans_data',
		'default_timespan'
		])

	endpoint = 'countries'
	url = 'http://bit.ly/1V0HZR7'
	timespan_tuples = [(4, 'month'), (3, 'week')]
	timespans = [lnk.bitly.stats.Stats.Timespan(s, u) for s, u in timespan_tuples]
	first_level = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	second_level = ecstasy.beautify('   <-> {0}: {1}', ecstasy.Color.Yellow)
	forever = lnk.bitly.stats.Stats.Timespan(-1, 'day')
	forever_data = request_stats(url, endpoint, forever)
	timespans_data = [request_stats(url, endpoint, i) for i in timespans]

	default_timespan = lnk.bitly.stats.Stats.Timespan(1, 'month')
	with lnk.config.Manager('bitly', write=True) as manager:
		settings = manager['commands']['stats']['settings']
		old = (settings['span'], settings['unit'])
		settings['span'] = default_timespan.span
		settings['unit'] = default_timespan.unit

	stats = lnk.bitly.stats.Stats(raw=True)
	info = lnk.bitly.info.Info(raw=True)

	def finalize():
		with lnk.config.Manager('bitly', write=True) as manager:
			settings = manager['commands']['stats']['settings']
			settings['span'] = old[0]
			settings['unit'] = old[1]

	request.addfinalizer(finalize)

	return Fixture(stats,
				   info,
				   endpoint,
				   url,
				   timespan_tuples,
				   timespans,
				   forever,
				   first_level,
				   second_level,
				   forever_data,
				   timespans_data,
				   default_timespan)


def test_format_makes_lines_pretty(fixture):
	result = fixture.stats.format(None, 'foo', 'bar', None)
	expected = fixture.second_level.format('foo', 'bar')

	assert result == expected


def test_countries_leaves_countries_short(fixture):
	result = fixture.stats.format('countries', 'DE', 123, False)
	expected = fixture.second_level.format('DE', '123')

	assert result == expected


def test_format_expands_countries(fixture):
	result = fixture.stats.format('countries', 'DE', 123, True)
	expected = fixture.second_level.format('Germany', '123')

	assert result == expected

def test_format_handles_unknown_countries(fixture):
	result = fixture.stats.format('countries', 'None', 123, True)
	expected = fixture.second_level.format('Other', '123')

	assert result == expected


def test_format_title_cases_direct(fixture):
	result = fixture.stats.format(None, 'direct', 666, None)
	expected = fixture.second_level.format('Direct', '666')

	assert result == expected

def test_request_format_is_correct(fixture):
	fixture.stats.queue.put((
		fixture.url,
		'countries',
		fixture.forever,
		{
		'unit': fixture.forever.unit,
		'units': fixture.forever.span,
		'link': fixture.url
		}))
	results = {fixture.endpoint: []}
	fixture.stats.request(results)
	result = results[fixture.endpoint][0]

	assert isinstance(result, dict)
	assert 'timespan' in result
	assert isinstance(result['timespan'], fixture.stats.Timespan)
	assert 'data' in result
	assert isinstance(result['data'], list)


def test_requests_countries_well(fixture):
	fixture.stats.queue.put((
		fixture.url,
		'countries',
		fixture.forever,
		{
		'unit': fixture.forever.unit,
		'units': fixture.forever.span,
		'link': fixture.url
		}))
	result = {fixture.endpoint: []}
	fixture.stats.request(result)
	result = result[fixture.endpoint][0]

	assert result == fixture.forever_data

def test_requests_referrers_well(fixture):
	fixture.stats.queue.put((
		fixture.url,
		'referrers',
		fixture.forever,
		{
		'unit': fixture.forever.unit,
		'units': fixture.forever.span,
		'link': fixture.url
		}))
	result = {'referrers': []}
	fixture.stats.request(result)
	result = result['referrers'][0]
	expected = request_stats(fixture.url, 'referrers', fixture.forever)

	assert result == expected

def test_requests_clicks_well(fixture):
	fixture.stats.queue.put((
		fixture.url,
		'clicks',
		fixture.forever,
		{
		'unit': fixture.forever.unit,
		'units': fixture.forever.span,
		'link': fixture.url
		}))
	result = {'clicks': []}
	fixture.stats.request(result)
	result = result['clicks'][0]
	expected = request_stats(fixture.url, 'clicks', fixture.forever)

	assert result == expected

def test_requests_timespan_well(fixture):
	fixture.stats.queue.put((
		fixture.url,
		fixture.endpoint,
		fixture.timespans[0],
		{
		'unit': fixture.timespans[0].unit,
		'units': fixture.timespans[0].span,
		'link': fixture.url
		}))
	results = {fixture.endpoint: []}
	fixture.stats.request(results)

	assert results[fixture.endpoint][0] == fixture.timespans_data[0]


def test_listify_sets_None_if_no_items(fixture):
	data = copy.deepcopy(fixture.forever_data)
	data['data'] = []
	result = fixture.stats.listify(None, [data], False)
	header = fixture.first_level.format('Since forever')
	expected = ['{0}: None'.format(header)]

	assert result == expected


def test_listify_handles_clicks_well(fixture):
	data = copy.deepcopy(fixture.forever_data)
	data['data'] = 123
	result = fixture.stats.listify(None, [data], False)
	header = fixture.first_level.format('Since forever')
	expected = ['{0}: 123'.format(header)]

	assert result == expected


def test_listify_handles_lists_well(fixture):
	data = copy.deepcopy(fixture.forever_data)
	result = fixture.stats.listify(None, [data], False)
	header = fixture.first_level.format('Since forever')
	if fixture.forever_data['data']:
		expected = ['{0}:'.format(header)]
		for i in fixture.forever_data['data']:
			# A way of not having to pop the clicks
			clicks = i['clicks']
			keys = i.keys()
			keys.remove('clicks')
			assert len(keys) == 1
			key = i[keys[0]]
			line = fixture.second_level.format(key, clicks)
			expected.append(line)
	else:
		expected = ['{0}: None'.format(header)]

	assert result == expected


def test_get_header_formats_timespans_well(fixture):
	result = fixture.stats.get_header(4, 'weeks')
	expected = fixture.first_level.format('Last 4 weeks:')

	assert result == expected


def test_get_header_handles_forever_well(fixture):
	result = fixture.stats.get_header(-1, None)
	expected = fixture.first_level.format('Since forever:')

	assert result == expected


def test_get_header_removes_unit_if_1(fixture):
	result = fixture.stats.get_header(1, 'day')
	expected = fixture.first_level.format('Last day:')

	assert result == expected


def test_get_header_handles_years_well(fixture):
	result = fixture.stats.get_header(12, 'months')
	expected = fixture.first_level.format('Last year:')

	assert result == expected


def test_get_header_adds_plural_s_if_multiple_years(fixture):
	result = fixture.stats.get_header(24, 'months')
	expected = fixture.first_level.format('Last 2 years:')

	assert result == expected


def test_lineify_formats_headers_well(fixture):

	data = {fixture.endpoint: [copy.deepcopy(fixture.forever_data)]}
	result = fixture.stats.lineify(data, False)

	assert 'Countries:' in result


def test_get_timespans_removes_duplicates(fixture):
	timespans = list(fixture.timespan_tuples)
	timespans += [fixture.timespan_tuples[0]] * 10
	result = fixture.stats.get_timespans(timespans, False)

	assert result == set(fixture.timespans)


def test_get_timespans_picks_default_timespan_if_no_times(fixture):
	result = fixture.stats.get_timespans([], False)

	assert result == set([fixture.default_timespan])


def test_get_timespans_handles_forever_well(fixture):
	result = fixture.stats.get_timespans([], True)

	assert result == set([fixture.forever])


def test_get_timespans_handles_year_well(fixture):
	result = fixture.stats.get_timespans(((1, 'year'),), False)
	expected = set([fixture.stats.Timespan(12, 'months')])

	assert result == expected


def test_get_timespans_works(fixture):
	result = fixture.stats.get_timespans(fixture.timespan_tuples, False)

	assert result == set(fixture.timespans)


def test_get_stats_works_for_single_endpoint(fixture):
	result = fixture.stats.get_stats(fixture.url,
									   [fixture.forever],
									   [fixture.endpoint])
	expected = {fixture.endpoint: [fixture.forever_data]}

	assert result == expected

def test_get_stats_works_for_many_timespans(fixture):
	result = fixture.stats.get_stats(fixture.url,
									   fixture.timespans,
									   [fixture.endpoint])

	assert isinstance(result, dict)
	assert fixture.endpoint in result
	assert isinstance(result[fixture.endpoint], list)

	expected = sorted(fixture.timespans_data)
	result = sorted(result[fixture.endpoint])

	assert result == expected


def test_get_stats_handles_plural_s_in_timespan_well(fixture):
	timespans = copy.deepcopy(fixture.timespans)
	timespans[0] = fixture.stats.Timespan(timespans[0].span,
										  timespans[0].unit + 's')
	result = fixture.stats.get_stats(fixture.url,
								  	   timespans,
								       [fixture.endpoint])
	data = copy.deepcopy(fixture.timespans_data)
	data[0]['timespan'] = timespans[0]

	assert isinstance(result, dict)
	assert fixture.endpoint in result
	assert isinstance(result[fixture.endpoint], list)

	for i, j in zip(data, result[fixture.endpoint]):
		i['data'].sort()
		j['data'].sort()

	result = sorted(result[fixture.endpoint])
	expected = sorted(data)

	assert result == expected


def test_get_stats_works_for_many_endpoints(fixture):
	endpoints = ['clicks', 'referrers', 'countries']
	result = fixture.stats.get_stats(fixture.url,
									   [fixture.forever],
									   endpoints)

	expected = {fixture.endpoint: [fixture.forever_data]}
	endpoints.remove(fixture.endpoint)
	for endpoint in endpoints:
		data = request_stats(fixture.url, endpoint, fixture.forever)
		expected[endpoint] = [data]

	assert result == expected


def test_fetch_works_for_single_url(fixture):
	result = fixture.stats.fetch([fixture.endpoint],
								 [],
								 fixture.timespan_tuples,
								 False,
								 None,
								 False,
								 False,
								 [fixture.url])
	expected = ['URL: {0}'.format(fixture.url)]
	data = copy.deepcopy(fixture.timespans_data)
	data = {fixture.endpoint: data}
	expected += fixture.stats.lineify(data, False)

	assert len(result) == 1
	assert sorted(result[0]) == sorted(expected)


def test_fetch_limits_well(fixture):
	result = fixture.stats.fetch([fixture.endpoint],
								 [],
								 [],
								 True,
								 1,
								 False,
								 False,
								 [fixture.url])
	expected = ['URL: {0}'.format(fixture.url)]
	data = copy.deepcopy(fixture.forever_data)
	while len(data['data']) > 1:
		data['data'].pop()
	assert len(data['data']) == 1
	data = {fixture.endpoint: [data]}
	expected += fixture.stats.lineify(data, False)

	assert len(result) <= 1
	assert sorted(result[0]) == sorted(expected)

def test_fetch_works_for_many_urls(fixture):
	urls = [fixture.url, 'http://bit.ly/1Km6CB1']
	result = fixture.stats.fetch([fixture.endpoint],
								 [],
								 [],
								 True,
								 None,
								 False,
								 False,
								 urls)
	print(fixture.forever_data)
	first = ['URL: {0}'.format(fixture.url)]
	data = {fixture.endpoint: [copy.deepcopy(fixture.forever_data)]}
	first += fixture.stats.lineify(data, False)

	second = ['URL: {0}'.format(urls[1])]
	data = request_stats(urls[1], fixture.endpoint, fixture.forever)
	data = {fixture.endpoint: [data]}
	second += fixture.stats.lineify(data, False)

	expected = [sorted(first), sorted(second)]

	assert [sorted(i) for i in result] == expected


def test_fetch_adds_info_well(fixture):
	result = fixture.stats.fetch([fixture.endpoint],
								 [],
								 fixture.timespan_tuples,
								 False,
								 None,
								 True,
								 False,
								 [fixture.url])
	expected = fixture.info.fetch([], [], False, [fixture.url])[0]
	data = {fixture.endpoint: fixture.timespans_data}
	expected += fixture.stats.lineify(data, False)

	assert len(result) == 1
	assert sorted(result[0]) == sorted(expected)
