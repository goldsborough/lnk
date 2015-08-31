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
		super(Link, self).__init__('link')
		self.already_copied = False
		self.raw = raw

	def fetch(self, copy, quiet, urls, pretty):
		result = []
		threads = []
		for url in urls:
			t = self.new_thread(self.shorten, result, copy, quiet, pretty, url)
			threads.append(t)
		self.join(threads)

		if self.raw:
			return result
		return self.boxify([result]) if pretty else '\n'.join(result)

	def shorten(self, result, copy, quiet, pretty, url):
		if not self.http.match(url):
			url = 'http://{0}'.format(url)
			if not quiet:
				errors.warn("Prepending 'http://' to '{0}'".format(url))
		short = self.request(url)
		formatted = self.copy(copy, short)
		if pretty:
			formatted = '{0} => {1}'.format(url, formatted)

		self.lock.acquire()
		result.append(formatted)
		self.lock.release()

	def request(self, url):
		response = self.get(self.endpoints['create'], dict(url=url))
		response = self.verify(response, "shorten url '{0}'".format(url))
		return response['shorturl']

	def copy(self, copy, url):
		if copy and not self.already_copied:
			self.already_copied = True
			pyperclip.copy(url)
			url = ecstasy.beautify('<{0}>'.format(url), ecstasy.Style.Bold)
		return url