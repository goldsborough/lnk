#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ecstasy
import os
import pyperclip
import pytest
import Queue
import requests
import threading

from collections import namedtuple

import tests.paths
import lnk.bitly.link

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()

LOCK = threading.Lock()
QUEUE = Queue.Queue()

def shorten(url):
	response = requests.get('{0}/shorten'.format(API),
							params=dict(access_token=ACCESS_TOKEN,
										longUrl=url))
	return response.json()['data']['url']

def shorten_fmt(destination):
	url = QUEUE.get()
	short = shorten(url)
	formatted = '{0} => {1}'.format(url, short)

	LOCK.acquire()
	destination.add(formatted)
	LOCK.release()


def expand(url):
	response = requests.get('{0}/expand'.format(API),
							params=dict(access_token=ACCESS_TOKEN,
										shortUrl=url))

	return response.json()['data']['expand'][0]['long_url']

def expand_fmt(destination):
	url = QUEUE.get()
	expanded = expand(url)
	formatted = '{0} => {1}'.format(url, expanded)

	LOCK.acquire()
	destination.add(formatted)
	LOCK.release()


@pytest.fixture(scope='module')
def fixture():
	Fixture = namedtuple('Fixture', [
		'link',
		'long',
		'short',
		'bold',
		'long_to_short',
		'short_to_long'
		])

	link = lnk.bitly.link.Link(raw=True)
	url = 'https://www.github.com/goldsborough/lnk'
	short = shorten(url)
	bold = ecstasy.beautify('<{0}>'.format(short), ecstasy.Style.Bold)
	long_to_short = '{0} => {1}'.format(url, short)
	short_to_long = '{0} => {1}'.format(short, url)

	return Fixture(link, url, short, bold, long_to_short, short_to_long)


def test_copy_copies_to_clipboard_if_copy_true(fixture):
	fixture.link.copy(True, fixture.short)

	assert pyperclip.paste() == fixture.short


def test_copy_copies_only_first_url(fixture):
	assert fixture.link.already_copied

	fixture.link.copy(True, 'a')
	fixture.link.copy(True, 'b')
	fixture.link.copy(True, 'c')

	assert pyperclip.paste() == fixture.short


def test_copy_copies_to_clipboard_if_copy_false(fixture):
	pyperclip.copy('original')
	fixture.link.copy(False, fixture.short)

	assert pyperclip.paste() == 'original'


def test_copy_makes_copied_url_bold(fixture):
	fixture.link.already_copied = False
	returned_url = fixture.link.copy(True, fixture.short)

	assert returned_url == fixture.bold


def test_get_short_shortens_well(fixture):
	result = fixture.link.get_short(fixture.long)

	assert result == fixture.short


def test_shorten_formats_well(fixture):
	result = []
	fixture.link.queue.put(fixture.long)
	fixture.link.shorten(result, False)

	assert result[0] == fixture.long_to_short


def test_get_long_expands_well(fixture):
	result = fixture.link.get_long(fixture.short)

	assert result == fixture.long


def test_expand_formats_well(fixture):
	result = []
	fixture.link.queue.put(fixture.short)
	fixture.link.expand(result, False)

	assert result[0] == fixture.short_to_long


def test_shorten_urls_works_for_single_url(fixture):
	result = fixture.link.shorten_urls(False, True, [fixture.long])

	assert result[0] == fixture.long_to_short


def test_shorten_urls_works_for_many_urls(fixture):
	urls = [
		'http://facebook.com',
		'http://google.com',
		'http://python.org'
	]
	result = set(fixture.link.shorten_urls(False, True, urls))
	expected = set()
	threads = []
	for url in urls:
		QUEUE.put(url)
		thread = threading.Thread(target=shorten_fmt, args=(expected,))
		thread.daemon = True
		threads.append(thread)
		thread.start()

	for thread in threads:
		thread.join(timeout=10)

	print(expected, result)

	assert result == expected


def test_expand_urls_works_for_single_url(fixture):
	result = fixture.link.expand_urls(False, [fixture.short])

	assert result[0] == fixture.short_to_long


def test_expand_urls_works_for_many_urls(fixture):
	urls = [
		'http://bit.ly/1O5MWni',
		'http://bit.ly/1NWAPWn',
		'http://bit.ly/1Jjoc4B'
	]
	result = fixture.link.expand_urls(False, urls)
	expected = set()
	threads = []
	for url in urls:
		QUEUE.put(url)
		thread = threading.Thread(target=expand_fmt, args=(expected,))
		thread.daemon = True
		thread.start()
		threads.append(thread)

	for thread in threads:
		thread.join(timeout=10)

	print(result, expected)

	assert set(result) == expected


def test_shorten_urls_warns_about_url_without_protocol(fixture, capsys):
	fixture.link.shorten_urls(False, False, ['google.com'])
	out = capsys.readouterr()

	assert out
	assert out[0].startswith("\aWarning: Prepending 'http://' to")


def test_fetch_works(fixture):
	result = fixture.link.fetch(False,
								True,
								[fixture.short],
								[fixture.long],
								False)

	assert result == [fixture.long_to_short, fixture.short_to_long]


def test_fetch_correct_output_if_raw_false_pretty_false(fixture):
	fixture.link.raw = False
	result = fixture.link.fetch(False,
								True,
								[fixture.short],
								[fixture.long],
								False)
	expected = '\n'.join([fixture.short_to_long, fixture.long_to_short])

	return result == expected
