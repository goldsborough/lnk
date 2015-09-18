#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import ecstasy
import httplib2
import oauth2client.file
import os.path
import pytest
import requests

from collections import namedtuple

import lnk.errors
import tests.paths
import lnk.googl.history

VERSION = 1
API = 'https://www.googleapis.com/urlshortener'
CREDENTIALS_PATH = os.path.join(tests.paths.CONFIG_PATH, 'credentials')

def timestamp(time_range, base=None):
	delta = {
		"minute": datetime.timedelta(minutes=1), 
		"hour": datetime.timedelta(hours=1), 
		"day": datetime.timedelta(days=1),
		"week": datetime.timedelta(weeks=1), 
		"month": datetime.timedelta(days=30.4368),
		"year": datetime.timedelta(days=365.242199)
	}
	offset = time_range[0] * delta[time_range[1]]
	base = base or datetime.datetime.now()

	return base - offset

def get_token():
	storage = oauth2client.file.Storage(CREDENTIALS_PATH)
	credentials = storage.get()
	if credentials.access_token_expired:
		credentials.refresh(httplib2.Http())
	token = credentials.access_token
	storage.put(credentials)

	return token


def request():
	token = get_token()
	url = '{0}/v{1}/url/history'.format(API, VERSION)
	urls = []
	data = {'nextPageToken': None}
	while 'nextPageToken' in data:
		response = requests.get(url,
								params={
								'start-token': data['nextPageToken'],
								'access_token': token
								})
		data = response.json()
		urls += data['items']

	return urls


def process(urls):
	return lnk.googl.history.History.process(urls)


def filter_urls(urls, start=None, end=None):
	if start:
		start = timestamp(start)
	else:
		start = datetime.datetime.min
	if end:
		end = timestamp(end)
	else:
		end = datetime.datetime.now()
	filtered = []
	for url in urls:
		if url.created >= start and url.created <= end:
			filtered.append(url)

	return filtered


@pytest.fixture(scope='module')
def fixture():
	
	Fixture = namedtuple('Fixture', [
		'history',
		'all_urls',
		'last',
		'last_urls',
		'ranges',
		'ranges_urls',
		'template',
		'url',
		'dummies',
		'short_dummies'
		])

	urls = process(request())

	history = lnk.googl.history.History(raw=True)

	last = [(4, 'week'), (5, 'month')]
	last_urls = [filter_urls(urls, i) for i in last]

	ranges = [(5, 'month', 4, 'week'), (7, 'year', 1, 'day')]
	ranges_urls = [filter_urls(urls, i[:2], i[2:]) for i in ranges]

	template = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	short = 'http://goo.gl/fDwgtb'
	expanded = 'http://python.org/'
	url = history.Url(short, expanded, datetime.datetime.now())

	short_dummies = ['a', 'b', 'c', 'd', 'e']
	dummies = [
		history.Url('a', 'aa', datetime.datetime(1997, 7, 26)),
		history.Url('b', 'bb', datetime.datetime(2009, 5, 23)),
		history.Url('c', 'cc', datetime.datetime(2012, 12, 21)),
		history.Url('d', 'dd', datetime.datetime(2015, 6, 3)),
		history.Url('e', 'ee', datetime.datetime(2015, 9, 15))
	]


	return Fixture(history,
				   urls,
				   last,
				   last_urls,
				   ranges,
				   ranges_urls,
				   template,
				   url,
				   dummies,
				   short_dummies)


def test_initializes_well(fixture):
	assert hasattr(fixture.history, 'raw')
	assert hasattr(fixture.history, 'delta')
	assert isinstance(fixture.history.delta, dict)
	values = fixture.history.delta.values()
	assert all(isinstance(i, datetime.timedelta) for i in values)

def test_request_works(fixture):
	expected = request()
	result = fixture.history.request()

	assert result == expected


def test_lineify_picks_short_if_pretty_false(fixture):
	result = fixture.history.lineify(fixture.url, False, False, False)

	assert result == fixture.url.short


def test_lineify_prettifies_if_pretty_true(fixture):
	result = fixture.history.lineify(fixture.url, False, False, True)
	expected = fixture.template.format(fixture.url.short)

	assert result == expected


def test_lineify_returns_only_expanded_if_expanded_true(fixture):
	result = fixture.history.lineify(fixture.url, True, False, False)

	assert result == fixture.url.long


def test_lineify_returns_both_if_both_true(fixture):
	result = fixture.history.lineify(fixture.url, False, True, False)
	expected = '{0} => {1}'.format(fixture.url.short, fixture.url.long)

	assert result == expected


def test_listify_works(fixture):
	result = fixture.history.listify([fixture.url],
									 None,
									 True,
									 False,
									 False)
	expected = [fixture.url.long]

	assert result == expected

def test_listify_limits_well(fixture):
	urls = [fixture.url] + fixture.dummies
	result = fixture.history.listify(urls,
									 1,
									 False,
									 False,
									 False)
	expected = [fixture.url.short]

	assert result == expected


def test_filter_works(fixture):
	begin = datetime.datetime(2008, 1, 3)
	end = datetime.datetime(2013, 4, 7)
	result = fixture.history.filter(fixture.dummies, begin, end)
	expected = fixture.dummies[1:3]

	assert result == expected


def test_get_date_works(fixture):
	now = datetime.datetime.now()
	result = fixture.history.get_date((1, 'minute'), now)
	expected = now - datetime.timedelta(minutes=1)

	assert result == expected


def test_get_date_works_works_if_endswith_s(fixture):
	now = datetime.datetime.now()
	result = fixture.history.get_date((1, 'minutes'), now)
	expected = now - datetime.timedelta(minutes=1)

	assert result == expected


def test_get_boundaries_works(fixture):
	base = datetime.datetime.now()
	result = fixture.history.get_boundaries(fixture.ranges[0], base)
	expected = (timestamp(fixture.ranges[0][:2], base),
				timestamp(fixture.ranges[0][2:], base))

	assert result == expected


def test_get_boundaries_throws_for_invalid_range(fixture):
	base = datetime.datetime.now()
	invalid_range = (4, 'days', 10, 'weeks')

	with pytest.raises(lnk.errors.UsageError):
		fixture.history.get_boundaries(invalid_range, base)


def test_last_works_for_single_range(fixture):
	result = fixture.history.last(fixture.dummies,
								  [fixture.last[1]],
								  None,
								  False,
								  False,
								  False)
	expected = fixture.short_dummies[3:]

	assert result == expected

def test_last_works_for_many_ranges(fixture):
	result = fixture.history.last(fixture.dummies,
								  fixture.last,
								  None,
								  False,
								  False,
								  False)
	expected = [fixture.short_dummies[4]]
	expected += fixture.short_dummies[3:]

	assert result == expected

def test_ranges_works_for_single_range(fixture):
	result = fixture.history.ranges(fixture.dummies,
									[fixture.ranges[0]],
									None,
									False,
									False,
									False)
	expected = [fixture.short_dummies[3]]

	assert result == expected

def test_ranges_works_for_many_ranges(fixture):
	result = fixture.history.ranges(fixture.dummies,
									fixture.ranges,
									None,
									False,
									False,
									False)
	expected = [fixture.dummies[3].short]
	expected += fixture.short_dummies[1:]

	assert result == expected


def test_forever_works(fixture):
	result = fixture.history.forever(fixture.dummies,
									 None,
									 False,
									 False,
									 False)
	expected = fixture.short_dummies

	assert result == expected


def test_pretty_works_for_forever(fixture):
	result = fixture.history.forever(fixture.dummies,
									 None,
									 False,
									 False,
									 True)
	expected = ['Since forever:']
	expected += [fixture.template.format(i) for i in fixture.short_dummies]

	assert result == expected + ['']

def test_pretty_works_for_last(fixture):
	result = fixture.history.last(fixture.all_urls,
								  fixture.last,
								  None,
								  False,
								  False,
								  True)
	expected = []
	for timespan, urls in zip(fixture.last, fixture.last_urls):
		span = '{0} '.format(timespan[0]) if timespan[0] > 1 else ''
		header = 'Last {0}{1}:'.format(span, timespan[1])
		if not urls:
			header += ' None'
		expected.append(header)
		for item in urls:
			expected.append(fixture.template.format(item.short))
		expected.append('')

	assert result == expected

def test_pretty_works_for_ranges(fixture):
	result = fixture.history.ranges(fixture.all_urls,
									fixture.ranges,
									None,
									False,
									False,
									True)
	expected = []
	for timespan, urls in zip(fixture.ranges, fixture.ranges_urls):
		header = 'Between {0} {1} '.format(timespan[0], timespan[1])
		header += 'and {0} {1} ago:'.format(timespan[2], timespan[3])
		if not urls:
			header += ' None'
		expected.append(header)
		for item in urls:
			expected.append(fixture.template.format(item.short))
		expected.append('')

	assert result == expected


def test_ranges_header_removes_unit_if_both_equal(fixture):
	time_range = (7, 'days', 2, 'days')
	result = fixture.history.ranges_header(time_range, True)
	expected = 'Between 7 and 2 days ago:'

	assert result == expected


def test_ranges_handles_empty_results_well(fixture):
	timespan = fixture.ranges[0]
	result = fixture.history.ranges([],
									[timespan],
									None,
									False,
									False,
									True)
	header = 'Between {0} {1} '.format(timespan[0], timespan[1])
	header += 'and {0} {1} ago:'.format(timespan[2], timespan[3])
	header += ' None'
	expected = [header, '']

	assert sorted(result) == sorted(expected)


def test_fetch_works_only_for_forever(fixture):
	result = fixture.history.fetch(None, None, True, None, False, False, False)
	expected = [i.short for i in fixture.all_urls]

	assert sorted(result) == sorted(expected)


def test_fetch_removes_last_line(fixture):
	result = fixture.history.fetch(None, None, True, None, False, False, True)
	expected = len(['Since forever:'] + [i.short for i in fixture.all_urls])

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
	expected = [fixture.all_urls] + fixture.ranges_urls + fixture.last_urls
	expected = [j.short for i in expected for j in i]

	assert len(result) == len(expected)
	assert sorted(result) == sorted(expected)


def test_fetch_limits_well(fixture):
	result = fixture.history.fetch(None, None, True, 3, False, False, False)
	expected = [i.short for i in fixture.all_urls[:3]]

	assert len(result) <= 3
	assert sorted(result) == sorted(expected)
