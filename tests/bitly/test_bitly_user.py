#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ecstasy
import os
import pytest
import random
import requests
import time

from collections import namedtuple

import tests.paths
import lnk.bitly.user

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()


def request_info():
	response = requests.get('{0}/user/info'.format(API),
							params=dict(access_token=ACCESS_TOKEN))

	return response.json()['data']

def request_history():
	response = requests.get('{0}/user/link_history'.format(API),
							params=dict(access_token=ACCESS_TOKEN))
	data = response.json()['data']['link_history']
	history = [i['link'] for i in data]
	history.sort()

	return history


@pytest.fixture(scope='module')
def fixture():
	Fixture = namedtuple('Fixture', [
		'user',
		'only',
		'hide',
		'sets',
		'all',
		'selected',
		'formatted',
		'template',
		'history'
		])

	user = lnk.bitly.user.User(raw=True)
	user.parameters['access_token'] = ACCESS_TOKEN
	user.history.parameters['access_token'] = ACCESS_TOKEN
	only = ['name', 'date', 'privacy']
	hide = ['login']
	sets = {
	    'name': 'full_name',
	    'date': 'member_since',
	    'privacy': 'default_link_privacy',
	}
	data = request_info()
	selected = dict((k, data[k]) for k in data if k in sets.values())
	formatted = []
	for key, value in selected.items():
		if isinstance(value, list):
			formatted.append('{0}: '.format(key.title()))
			formatted += [' + {0}'.format(t) for t in value]
		else:
			formatted.append(user.format(key, value))
	formatted.sort()
	template = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)
	history = request_history()

	return Fixture(user,
				   only,
				   hide,
				   sets,
				   data,
				   selected,
				   formatted,
				   template,
				   history)


def test_initializes_well(fixture):
	
	assert hasattr(fixture.user, 'history')
	assert hasattr(fixture.user, 'keys')
	assert hasattr(fixture.user, 'list_item')
	assert isinstance(fixture.user.keys, dict)
	assert 'full_name' in fixture.user.keys
	assert fixture.user.keys['full_name'] == 'Full Name'


def test_order_works(fixture):
	expected = [
		'full_name',
		'member_since',
		'default_link_privacy'
	]

	keys = list(fixture.selected.keys())
	random.shuffle(keys)
	shuffled = dict((key, fixture.selected[key]) for key in keys)
	result = fixture.user.order(shuffled, fixture.sets.values())

	assert list(result.keys()) == expected


def test_request_works(fixture):
	result = fixture.user.request(fixture.sets)
	expected = fixture.user.order(fixture.selected, fixture.sets)

	assert result == expected

def test_format_maps_keys_well(fixture):
	result = fixture.user.format('full_name', 'Satan')
	expected = 'Full Name: Satan'
	assert result == expected

	result = fixture.user.format('default_link_privacy', 'public')
	expected = 'Link privacy: public'
	assert result == expected


def test_format_handles_None_well(fixture):
	result = fixture.user.format('full_name', None)
	expected = 'Full Name: None'

	assert result == expected


def test_format_parses_times_well(fixture):
	now = time.time()
	result = fixture.user.format('member_since', now)
	expected = 'Member Since: {0}'.format(time.ctime(now))

	assert result == expected

def test_format_accounts_works(fixture):
	accounts = [
		dict(account_type='twitter', account_name='batman'),
		dict(account_type='facebook', account_name='Bat Man')
	]
	result = fixture.user.format_accounts(accounts)
	expected = [
		'Share Accounts:',
		fixture.template.format('Twitter: @batman'),
		fixture.template.format('Facebook: Bat Man')
	]

	assert result == expected

def test_lineify_works_without_lists(fixture):
	result = fixture.user.lineify(fixture.selected, False)
	expected = [fixture.user.format(k, v) for k, v in fixture.selected.items()]	

	assert result == expected

def test_lineify_works_with_lists(fixture):
	data = fixture.selected.copy()
	data['full_name'] = ['a', 'b', 'c']
	result = fixture.user.lineify(data, False)
	expected = []
	for key, value in data.items():
		if isinstance(value, list):
			expected.append(fixture.user.format(key))
			expected += [fixture.template.format(i) for i in value]
		else:
			expected.append(fixture.user.format(key, value))

	assert result == expected

def test_lineify_hides_empty_if_wanted(fixture):
	result = fixture.user.lineify({'login': None}, True)

	# better than isinstance(..., list) + 'assert result'
	assert result == []


def test_get_history_works(fixture):
	expected = [fixture.template.format(i) for i in fixture.history]
	result = fixture.user.get_history()
	result.sort()

	assert result == expected


def test_fetch_works_without_history(fixture):
	result = fixture.user.fetch(fixture.only,
								fixture.hide,
								True,
								False,
								False)
	result.sort()

	assert result == fixture.formatted


def test_fetch_works_with_history(fixture):
	result = fixture.user.fetch(fixture.only,
								fixture.hide,
								True,
								True,
								False)
	result[0].sort()
	result[1].sort()
	history = [fixture.template.format(i) for i in fixture.history]
	history.sort()
	expected = [fixture.formatted, history]

	assert result == expected
