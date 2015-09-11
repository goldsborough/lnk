#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click

from datetime import datetime

from googl.command import Command

def echo(*args):
	click.echo(Info().fetch(*args))

class Info(Command):

	def __init__(self, raw=False):
		super(Info, self).__init__('info')

		self.raw = raw
		self.sets = self.config['sets']
		self.parameters['projection'] = 'FULL'

	def fetch(self, only, hide, urls):
		sets = self.filter(only, hide)

		result = []
		threads = []
		for url in urls:
			self.queue.put(url.strip())
			t = self.new_thread(self.request, sets.values(), result)
			threads.append(t)
		self.join(threads)

		return result if self.raw else self.boxify(result)

	def filter(self, only, hide):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for key in hide:
			del sets[key]
		return sets

	def request(self, sets, result):
		url = self.queue.get()
		response = self.get(self.endpoints['info'], dict(shortUrl=url))
		response = self.verify(response,
							   "retrieve information for '{0}'".format(url))

		selection = {key : data[key] for key in data if key in sets}
		lines = self.lineify(url, selection, hide_empty)

		self.lock.acquire()
		result.append(lines)
		self.lock.release()

	def lineify(self, url, data): 
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			if key == 'created':
				value = datetime.strptime(t[:t.find('.')], '%Y-%m-%dT%H:%M:%S')
			lines.append(self.format(key, value))
		return lines
