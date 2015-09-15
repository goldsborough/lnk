#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ecstasy
import os
import pytest
import Queue
import requests
import threading

from collections import namedtuple

import tests.paths
import bitly.stats

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()

@pytest.fixture(scope='module')
def fixture():
	Fixture = namedtuple('Fixture', [
		'stats',
		'urls',
		'first_level',
		'second_level'
		])

	stats = bitly.stats.Stats(raw=True)
	urls = ['http://bit.ly/1OQM9nA', 'http://bit.ly/1Km6CB1']
	first_level = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	second_level = ecstasy.beautify(' <-> {0}', ecstasy.Color.Yellow)

	return Fixture(stats,
					urls,
					first_level,
					second_level)


def test_lines_pretty(fixture):
	pass


def test_countries_leaves_countries_short(fixture):
	pass


def test_countries(fixture):
	pass


def test_cases_direct(fixture):
	pass


def test_requests_well(fixture):
	pass


def test_timespans_well(fixture):
	pass


def test_None_if_no_items(fixture):
	pass


def test_clicks_well(fixture):
	pass


def test_lists_well(fixture):
	pass


def test_headers_well(fixture):
	pass


def test_removes_duplicates(fixture):
	pass


def test_picks_default_timespan_if_no_times(fixture):
	pass


def test_handles_forever_well(fixture):
	pass


def test_handles_year_well(fixture):
	pass


def test_works(fixture):
	pass


def test_works_for_single_endpoint(fixture):
	pass


def test_handles_plural_s_in_timespan_well(fixture):
	pass


def test_works_for_many_endpoints(fixture):
	pass


def test_for_single_url(fixture):
	pass


def test_for_many_urls(fixture):
	pass


def test_info_well(fixture):
	pass


def test_well(fixture):
	pass
