#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
		'urls'
		])

	stats = bitly.stats.Stats(raw=True)
	urls = ['http://bit.ly/1OQM9nA', 'http://bit.ly/1Km6CB1']

	return Fixture(stats, urls)


def test_bitly_stats_requests_well(fixture):
	pass