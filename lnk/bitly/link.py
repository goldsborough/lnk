#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import ecstasy
import pyperclip
import Queue
import threading

import errors

from command import Command

def echo(*args):
	click.echo(Link().fetch(*args))

class Link(Command):

	def __init__(self, raw=False):
		super(Link, self).__init__('bitly', 'link')
		self.already_copied = False
		self.raw = raw
		self.queue = Queue.Queue()
		self.lock = threading.Lock()

	def fetch(self, copy, quiet, expand, shorten):
		result = self.shorten_urls(copy, quiet, shorten)
		result += self.expand_urls(copy, expand)

		return result if self.raw else self.boxify([result])

	def expand_urls(self, copy, urls):
		lines = []
		self.parameters['longUrl'] = None
		for url in urls:
			expanded = self.get_long(url)
			expanded = self.copy(copy, expanded)
			lines.append('{0} => {1}'.format(url, expanded))
		return lines

	def shorten_urls(self, copy, quiet, urls):
		lines = []
		for url in urls:
			if not self.http.match(url):
				url = 'http://{0}'.format(url)
				if not quiet:
					errors.warn("Prepending 'http://' to {0}".format(url))
			self.shorten(lines, url, copy)
			#self.queue.put(url)
			#args = (lines, copy)
			#thread = threading.Thread(target=self.shorten, args=args)
			#thread.setDaemon(True)
			#thread.start()
		#self.queue.join()
		return lines

	def shorten(self, lines, url, copy):
		#url = self.queue.get()
		short = self.get_short(url)
		short = self.copy(copy, short)
		#self.lock.acquire()
		lines.append('{0} => {1}'.format(url, short))
		#self.lock.release()
		#self.queue.task_done()

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
