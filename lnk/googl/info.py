#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click

from datetime import datetime

import abstract
import beauty

from googl.command import Command

def echo(*args):
	click.echo(Info().fetch(*args))

class Info(Command):

	def __init__(self, raw=False):
		super(Info, self).__init__('info')

		self.raw = raw
		self.sets = self.config['sets']
		self.reverse = {value:key for key,value in self.sets.items()}

	def fetch(self, only, hide, urls):
		sets = abstract.filter_sets(self.sets, only, hide)
		result = []
		threads = []
		for url in urls:
			self.queue.put(url.strip())
			t = self.new_thread(self.get_info, sets.values(), result)
			threads.append(t)
		self.join(threads)

		return result if self.raw else beauty.boxify(result)

	def get_info(self, sets, result):
		url = self.queue.get()
		data = self.request(url)
		selection = {key : data[key] for key in data if key in sets}
		lines = self.lineify(url, selection)

		self.lock.acquire()
		result.append(lines)
		self.lock.release()

	def request(self, url):
		response = self.get(url, 'FULL')
		self.verify(response, "get information for '{0}'".format(url))

		return response

	def lineify(self, url, data): 
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			lines.append(self.format(key, value))

		return lines

	def format(self, key, value):
		key = self.reverse[key]
		if key == 'created':
			# Ignore the irrelevant part of the ISO format
			relevant = value[:value.find('.')]
			parsed = datetime.strptime(relevant, '%Y-%m-%dT%H:%M:%S')
			value = parsed.ctime()

		return '{0}: {1}'.format(key.title(), value)
