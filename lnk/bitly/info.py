#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import time

from command import Command

def echo(*args):
	click.echo(Info().fetch(*args))

class Info(Command):

	def __init__(self, raw=False):
		super(Info, self).__init__('bitly', 'info')

		self.raw = raw
		self.sets = self.config['sets']
		self.reverse = {value:key for key,value in self.sets.items()}

	def fetch(self, only, hide, hide_empty, urls):
		sets = self.filter(only, hide)

		result = []
		for url in urls:
			data = self.get(url, sets.values())
			lines = self.lineify(url, data, hide_empty)
			result.append(lines)

		return result if self.raw else self.boxify(result)

	def filter(self, only, hide):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for key in hide:
			del sets[key]
		return sets

	def get(self, url, sets):
		data = self.get_info(url)
		data.update(self.get_history(url))
		return {key : data[key] for key in data if key in sets}

	def get_info(self, url):
		self.parameters['shortUrl'] = url
		response = self.request(self.endpoints['info'])
		self.verify(response,
				   "retrieve information for '{0}'".format(url),
				   'info')

		return response['data']['info'][0]

	def get_history(self, url):
		response = self.request(self.endpoints['history'])
		self.verify(response,
				   "retrieve history for '{0}'".format(url))
		return response['data']['link_history'][0]

	def lineify(self, url, data, hide_empty): 
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			if hide_empty and (value is None or value == ''):
				continue
			if isinstance(value, list):
				lines.append(self.format(key))
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

		return '{0}: {1}'.format(key.title(), value)
