#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import ecstasy
import pyperclip

import beauty
import errors

from googl.command import Command

def echo(*args):
	click.echo(Link().fetch(*args))

class Link(Command):

	def __init__(self, raw=False):
		super(Link, self).__init__('link')
		self.already_copied = False
		self.raw = raw

	def fetch(self, copy, quiet, expand, shorten, pretty):
		result = self.shorten_urls(copy, quiet, shorten)
		result += self.expand_urls(copy, expand)

		if self.raw:
			return result
		return beauty.boxify([result]) if pretty else '\n'.join(result)

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
					errors.warn("Prepending 'http://' to '{0}'".format(url))
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
		data = self.verify(response, "expand url '{0}'".format(url))

		if data['status'] in ['MALWARE', 'PHISHING']:
			errors.warn("Careful! goo.gl believes the url '{0}' is {1}"
						"!".format(data['longUrl']),
								   data['status'].lower())
		elif data['status'] == 'REMOVED':
			return '{0} (removed)'.format(data['longUrl'])

		return data['longUrl']

	def get_short(self, url):
		response = self.post(self.endpoints['shorten'], dict(longUrl=url))
		data = self.verify(response, "shorten url '{0}'".format(url))

		return data['id']

	def copy(self, copy, url):
		if copy and not self.already_copied:
			self.already_copied = True
			pyperclip.copy(url)
			url = ecstasy.beautify('<{0}>'.format(url), ecstasy.Style.Bold)

		return url
