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
		result = self.shorten_urls(copy, quiet, shorten)
		result += self.expand_urls(copy, expand)

		return result if self.raw else self.boxify([result])

	def expand_urls(self, copy, urls):
		lines = []
		threads = []
		for url in urls:
			self.queue.put(url)
			threads.append(self.new_thread(self.expand, lines, copy))
		self.join(threads)

		return lines

	def shorten_urls(self, copy, quiet, urls):
		lines = []
		threads = []
		for url in urls:
			if not self.http.match(url):
				url = 'http://{0}'.format(url)
				if not quiet:
					errors.warn("Prepending 'http://' to {0}".format(url))
			self.queue.put(url)
			threads.append(self.new_thread(self.shorten, lines, copy))
		self.join(threads)

		return lines

	def expand(self, lines, copy):
		url = self.queue.get()
		expanded = self.get_long(url)
		formatted = self.copy(copy, expanded)

		self.lock.acquire()
		lines.append('{0} => {1}'.format(url, formatted))
		self.lock.release()

	def shorten(self, lines, copy):
		url = self.queue.get()
		short = self.get_short(url)
		formatted = self.copy(copy, short)

		self.lock.acquire()
		lines.append('{0} => {1}'.format(url, formatted))
		self.lock.release()

	def get_long(self, url):
		response = self.get(self.endpoints['expand'], dict(shortUrl=url))
		response = self.verify(response,
							   "expand url '{0}'".format(url),
							   'expand')

		return response['expand'][0]['long_url']

	def get_short(self, url):
		response = self.get(self.endpoints['shorten'], dict(longUrl=url))
		response = self.verify(response, "shorten url '{0}'".format(url))
		return response['url']

	def copy(self, copy, url):
		if copy and not self.already_copied:
			pyperclip.copy(url)
			url = ecstasy.beautify('<{0}>'.format(url), ecstasy.Style.Bold)
			self.already_copied = True
		return url
