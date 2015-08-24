#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import ecstasy
import pyperclip

import errors

from command import Command

def echo(*args):
	click.echo(Link().fetch(*args))

class Link(Command):

	def __init__(self, raw=False):
		super(Link, self).__init__('bitly', 'link')
		self.already_copied = False
		self.raw = raw

	def fetch(self, copy, quiet, expand, shorten):
		result = self.shorten(copy, quiet, shorten) if shorten else []
		result += self.expand(copy, expand)

		return result if self.raw else self.boxify([result])

	def expand(self, copy, urls):
		lines = []
		del self.parameters['longUrl']
		for url in urls:
			expanded = self.get_long(url)
			expanded = self.copy(copy, expanded)
			lines.append('{0} => {1}'.format(url, expanded))
		return lines

	def shorten(self, copy, quiet, urls):
		lines = []
		for url in urls:
			if not self.http.match(url):
				url = 'http://{0}'.format(url)
				if not quiet:
					errors.warn("Prepending 'http://' to {0}".format(url))
			short = self.get_short(url)
			short = self.copy(copy, short)
			lines.append('{0} => {1}'.format(url, short))
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

	def copy(self, copy, url):
		if copy and not self.already_copied:
			pyperclip.copy(url)
			url = ecstasy.beautify('<{0}>'.format(url), ecstasy.Style.Bold)
			self.already_copied = True
		return url
