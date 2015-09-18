#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ecstasy
import pyperclip
import pytest
import requests
import threading

from collections import namedtuple

import tests.paths
import lnk.tinyurl.link

def shorten(url):
	response = requests.get('http://tiny-url.info/api/v1/create',
							params=dict(apikey='0BFA4A7B5BDD5BE7780C',
									 	format='json',
									 	provider='tinyurl_com',
									 	url=url))
	data = response.json()

	return data['shorturl']

@pytest.fixture(scope='module')
def fixture():
	Fixture = namedtuple('Fixture', ['link', 'long', 'short', 'formatted'])
	link = lnk.tinyurl.link.Link(raw=True)
	url = 'https://www.github.com/goldsborough/lnk'
	short = shorten(url)
	formatted = ecstasy.beautify('<{0}>'.format(short), ecstasy.Style.Bold)

	return Fixture(link, url, short, formatted)

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

	assert returned_url == fixture.formatted

def test_request_shortens_well(fixture):
	result = fixture.link.request(fixture.long)

	assert result == fixture.short

def test_shorten_formats_well(fixture):
	result = []
	fixture.link.shorten(result, False, True, True, fixture.long)
	expected = '{0} => {1}'.format(fixture.long, fixture.short)

	assert result[0] == expected

def test_shorten_warns_about_url_without_protocol(fixture, capsys):
	fixture.link.shorten([], False, False, False, 'google.com')
	out = capsys.readouterr()

	assert out
	assert out[0].startswith("\aWarning: Prepending 'http://' to")


def test_fetch_works_for_single_url(fixture):
	result = fixture.link.fetch(False, True, [fixture.long], False)

	assert result == [fixture.short]

def test_fetch_works_for_many_urls(fixture):
	urls = ['http://facebook.com', 'http://google.com', 'http://python.org']
	result = set(fixture.link.fetch(False, True, urls, False))

	expected = set()
	threads = []
	for url in urls:
		thread = threading.Thread(target=lambda u: expected.add(shorten(u)),
								  args=(url,))
		thread.daemon = True
		thread.start()
		threads.append(thread)

	for thread in threads:
		thread.join(timeout=10)

	assert result == expected

def test_fetch_correct_output_if_raw_false_pretty_false(fixture):
	fixture.link.raw = False
	urls = [fixture.long, 'http://python.org']
	result = fixture.link.fetch(False, True, urls, False)
	expected = '\n'.join([fixture.short, shorten(urls[1])])

	return result == expected
