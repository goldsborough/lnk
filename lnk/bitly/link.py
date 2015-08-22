#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import pyperclip

import errors

from command import Command

def echo(*args):
	click.echo(Link().fetch(*args))

class Link(Command):

	def __init__(self, *args):
		super(Link, self).__init__('bitly', 'link')

	def fetch(self, copy, quiet, expand, shorten):
		lines = self.expand(copy, expand) if expand else []
		lines += self.shorten(copy, quiet, shorten)
		return '\n'.join(lines)

	def expand(self, copy, urls):
		lines = []
		for url in urls:
			expanded = self.get_long(url)
			if copy:
				pyperclip.copy(expanded)
			lines.append('{0} -> {1}'.format(url, expanded))
		del self.parameters['shortUrl']
		return lines

	def shorten(self, copy, quiet, urls):
		lines = []
		for url in urls:
			if not self.http.match(url):
				url = 'http://{0}'.format(url)
				if not quiet:
					errors.warn("Prepending 'http://' to {0}".format(url))
			short = self.get_short(url)
			if copy:
				pyperclip.copy(short)
			lines.append('{0} -> {1}'.format(url, short))
		return lines

	def get_short(self, url):
		self.parameters['longUrl'] = url
		response = self.request(self.endpoints['shorten'])
		self.verify(response, 'shorten url')

		return response['data']['url']

	def get_long(self, url):
		self.parameters['shortUrl'] = url
		response = self.request(self.endpoints['expand'])
		self.verify(response, 'expand url', 'expand')

		return response['data']['expand'][0]['long_url']