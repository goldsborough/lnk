#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import time

import beauty

from bitly.command import Command

def echo(*args):
	click.echo(Info().fetch(*args))

class Info(Command):

	def __init__(self, raw=False):
		super(Info, self).__init__('info')

		self.raw = raw
		self.sets = self.config['sets']
		self.reverse = {value:key for key,value in self.sets.items()}

	def fetch(self, only, hide, hide_empty, urls):
		sets = self.filter(only, hide)

		result = []
		threads = []
		for url in urls:
			self.queue.put(url.strip())
			t = self.new_thread(self.request, sets.values(), result, hide_empty)
			threads.append(t)
		self.join(threads)

		return result if self.raw else beauty.boxify(result)

	def filter(self, only, hide):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for key in hide:
			del sets[key]
		return sets

	def request(self, sets, result, hide_empty):
		data = {}
		url = self.queue.get()

		first = self.new_thread(lambda: data.update(self.request_info(url)))
		second = self.new_thread(lambda: data.update(self.request_history(url)))

		first.join(timeout=10)
		second.join(timeout=10)

		selection = {key : data[key] for key in data if key in sets}
		lines = self.lineify(url, selection, hide_empty)

		self.lock.acquire()
		result.append(lines)
		self.lock.release()

	def request_info(self, url):
		response = self.get(self.endpoints['info'], dict(shortUrl=url))
		response = self.verify(response,
							   "retrieve information for '{0}'".format(url),
							   'info')

		return response

	def request_history(self, url):
		response = self.get(self.endpoints['history'], dict(link=url))
		response = self.verify(response,
				   			   "retrieve history for '{0}'".format(url))
		return response['link_history'][0]

	def lineify(self, url, data, hide_empty): 
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			if hide_empty and (not value and value != 0):
				continue
			if isinstance(value, list):
				lines.append(self.format(key, value))
				lines += [' - {0}'.format(i) for i in value]
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
			key = 'private'

		if isinstance(value, bool):
			value = 'Yes' if value else 'No'
		elif not value:
			value = 'None'
		elif isinstance(value, list):
			value = ''

		return '{0}: {1}'.format(key.title(), value)
