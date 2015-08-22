#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import errors

from command import Command

def handle(*args):
	Link(*args)

class Link(Command):

	def __init__(self, *args):
		super(Link, self).__init__('bitly', 'link')
		self.parse(*args)

	def parse(self, expand, shorten, quiet):
		lines = []
		for url in expand:
			lines.append('{0} -> {1}'.format(url, self.expand(url)))
		if expand:
			del self.parameters['shortUrl']
		for url in shorten:
			if not self.http.match(url):
				url = 'http://{0}'.format(url)
				if not quiet:
					errors.warn("Prepending 'http://' to {0}".format(url))
			lines.append('{0} -> {1}'.format(url, self.shorten(url)))

		click.echo('\n'.join(lines))

	def shorten(self, url):
		self.parameters['longUrl'] = url
		response = self.get(self.endpoints['shorten'])
		self.verify(response, 'shorten url')

		return response['data']['url']

	def expand(self, url):
		self.parameters['shortUrl'] = url
		response = self.get(self.endpoints['expand'])
		self.verify(response, 'expand url', 'expand')

		return response['data']['expand'][0]['long_url']