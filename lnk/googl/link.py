#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import apiclient.discovery
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
		response = self.get(url, what="expand url '{0}'".format(url))

		if response['status'] in ['MALWARE', 'PHISHING']:
			errors.warn("Careful! goo.gl believes the url '{0}' is {1}"
						"!".format(response['longUrl']),
								   response['status'].lower())
		elif response['status'] == 'REMOVED':
			return '{0} (removed)'.format(response['longUrl'])

		return response['longUrl']

	def get_short(self, url):
		api = self.get_api()
		request = api.insert(body=dict(longUrl=url))
		what = "shorten url '{0}'".format(url)
		response = self.execute(request, what)

		return response['id']

	def copy(self, copy, url):
		if copy and not self.already_copied:
			self.already_copied = True
			pyperclip.copy(url)
			url = ecstasy.beautify('<{0}>'.format(url), ecstasy.Style.Bold)

		return url
