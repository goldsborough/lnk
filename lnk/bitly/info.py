#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import time

import abstract
import beauty

from bitly.command import Command

def echo(*args):
	click.echo(Info().fetch(*args))

class Info(Command):

	def __init__(self, raw=False):
		super(Info, self).__init__('info')

		self.raw = raw
		self.sets = self.config['sets']
		self.reverse = {value:key for key, value in self.sets.items()}

	def fetch(self, only, hide, hide_empty, urls):
		sets = abstract.filter_sets(self.sets, only, hide)

		result = []
		threads = []
		for url in urls:
			self.queue.put(url.strip())
			t = self.new_thread(self.request, sets.values(), result, hide_empty)
			threads.append(t)
		self.join(threads)

		return result if self.raw else beauty.boxify(result)

	def request(self, sets, result, hide_empty):
		url = self.queue.get()
		data = self.request_info(url)
		data.update(self.request_history(url))

		selection = {key : data[key] for key in data if key in sets}
		lines = self.lineify(url, selection, hide_empty)

		with self.lock:
			result.append(lines)

	def request_info(self, url):
		response = self.get(self.endpoints['info'], dict(shortUrl=url))
		response = self.verify(response,
							   "retrieve information for '{0}'".format(url),
							   'info')

		return response

	def request_history(self, url):
		response = self.get(self.endpoints['history'], dict(link=url))
		response = self.verify(response,
				   			   "retrieve history for '{0}'".format(url),
				   			   'link_history')

		return response

	def lineify(self, url, data, hide_empty): 
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			if hide_empty and (not value and value != 0):
				continue
			if isinstance(value, list):
				lines.append(self.format(key, value))
				lines += [self.list_item.format(i) for i in value]
			else:
				lines.append(self.format(key, value))

		return lines

	def format(self, key, value):
		key = self.reverse[key]
		if key == 'created' or key == 'modified':
			value = time.ctime(value)
		elif key == 'user' and value is None:
			value = 'Not public'
		elif key == 'privacy':
			# the set is '--only privacy', but
			# want to display 'Private: ...'
			key = 'private'

		if isinstance(value, bool):
			value = 'Yes' if value else 'No'
		elif not value:
			value = 'None'
		elif isinstance(value, list):
			value = ''

		return '{0}: {1}'.format(key.title(), value)
