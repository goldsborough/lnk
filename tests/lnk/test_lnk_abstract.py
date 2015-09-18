#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import pytest
import requests
import threading

from collections import namedtuple

import tests.paths

import lnk.errors
import lnk.abstract

class Command(lnk.abstract.AbstractCommand):
	def __init__(self):
		super(Command, self).__init__('test', 'do')


@pytest.fixture(scope='module')
def fixture(request):
	Fixture = namedtuple('Fixture', [
		'command',
		'url',
		'version',
		'api',
		'endpoints',
		'settings',
		])

	directory = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(tests.paths.CONFIG_PATH, 'test.json')
	with open(os.path.join(directory, 'test.json'), 'rt') as source:
		config = json.load(source)
		with open(path, 'wt') as destination:
			json.dump(config, destination)

	def finalize():
		os.remove(path)

	request.addfinalizer(finalize)

	return Fixture(Command(),
				   config['url'],
				   config['version'],
				   '{0}/v{1}'.format(config['url'], config['version']),
				   config['commands']['do']['endpoints'],
				   config['commands']['do']['settings'])


def test_has_all_attributes(fixture):
	assert hasattr(fixture.command, 'url')
	assert hasattr(fixture.command, 'api')
	assert hasattr(fixture.command, 'config')
	assert hasattr(fixture.command, 'endpoints')
	assert hasattr(fixture.command, 'settings')


def test_attributes_are_correctly_set(fixture):
	assert fixture.command.url == fixture.url
	assert fixture.command.api == fixture.api
	assert fixture.command.endpoints == fixture.endpoints
	assert fixture.command.settings == fixture.settings


def test_default_GET_works_well(fixture):
	endpoint = fixture.endpoints[0]
	url = '{0}/{1}'.format(fixture.api, endpoint)

	response = fixture.command.get(endpoint)

	assert isinstance(response, requests.Response)
	assert response.request.method == 'GET'
	assert response.url == url

	response = fixture.command.get(endpoint,
								   parameters=dict(cats='awesome'))

	assert isinstance(response, requests.Response)
	assert response.request.method == 'GET'
	assert response.url == '{0}?cats=awesome'.format(url)


def test_default_POST_works_well(fixture):
	endpoint = fixture.endpoints[1]
	url = '{0}/{1}'.format(fixture.url, endpoint)

	response = fixture.command.post(endpoint)

	assert isinstance(response, requests.Response)
	assert response.request.method == 'POST'
	assert response.url == url

	response = fixture.command.post(endpoint,
									data=dict(cats='awesome'))

	assert isinstance(response, requests.Response)
	assert response.request.method == 'POST'

	assert response.request.body == 'cats=awesome'


def test_new_thread_sets_up_thread_well(fixture):
	def endless():
		while True:
			pass
	thread = fixture.command.new_thread(endless)

	assert isinstance(thread, threading.Thread)
	assert thread.is_alive()
	assert thread.daemon

	thread.join(0.1)


def test_exception_handling_for_threads_works(fixture):
	def throws():
		raise RuntimeError('Meh')
	thread = fixture.command.new_thread(throws)

	assert isinstance(thread, threading.Thread)
	
	thread.join()

	assert fixture.command.error is not None
	assert isinstance(fixture.command.error, RuntimeError)
	assert fixture.command.error.message == 'Meh'

	fixture.command.error = None


def test_join_method_works(fixture):
	threads = [fixture.command.new_thread(lambda: 1) for _ in range(10)]
	fixture.command.join(threads)

	assert not any(thread.is_alive() for thread in threads)


def test_join_method_throws_if_unjoinable(fixture):
	def blocks():
		while True:
			pass
	thread = fixture.command.new_thread(blocks)

	with pytest.raises(lnk.errors.InternalError):
		fixture.command.join([thread], timeout=0.1)


def test_join_method_re_raises_thread_exceptions(fixture):
	def throws():
		raise RuntimeError('Meh')
	thread = fixture.command.new_thread(throws)

	with pytest.raises(RuntimeError):
		fixture.command.join([thread])


def test_fetch_not_implemented(fixture):
	with pytest.raises(NotImplementedError):
		fixture.command.fetch()


def test_filter_sets_filters_well(fixture):
	base = dict((i, None) for i in 'abcde')
	only = ['a', 'c', 'e']
	result = lnk.abstract.filter_sets(base, only, [])

	assert sorted(result.keys()) == only


def test_filter_sets_hides_well(fixture):
	base = dict((i, None) for i in 'abcde')
	hide = ['a', 'c', 'e']
	result = lnk.abstract.filter_sets(base, [], hide)

	assert sorted(result.keys()) == ['b', 'd']
