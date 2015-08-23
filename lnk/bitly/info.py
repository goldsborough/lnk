#!/usr/bin/env python
#! -*- coding: utf-8 -*-

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

	def fetch(self, only, hide, urls):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for key in hide:
			del sets[key]

		lines = []
		for url in urls:
			data = self.get(url, sets)
			result = self.lineify(url, data, sets)
			lines.append(result)

		return lines if self.raw else self.boxify(lines)

	def lineify(self, url, data, sets): 
		line = 'URL: {0}'.format(url)
		lines = [line]
		for key, value in data.items():
			line = self.format(key, value)
			lines.append(line)
		return lines

	def format(self, key, value):
		key = self.reverse[key]
		if key == 'created':
			value = time.ctime(value)
		elif key == 'user' and value is None:
			value = 'Not public'

		return '{0}: {1}'.format(key.title(), value)

	def get(self, url, sets):
		self.parameters['shortUrl'] = url

		response = self.request(self.endpoints['info'])
		self.verify(response,
				   "retrieve information for '{0}'".format(url),
				   'info')

		response = response['data']['info'][0]
		return {k:v for k,v in response.items() if k in sets.values()}
