#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import time

from command import Command

def echo(*args):
	click.echo(Info().fetch(*args))

class Info(Command):

	def __init__(self):
		super(Info, self).__init__("bitly", "info")
		self.sets = self.config['sets']
		self.reverse = {value:key for key,value in self.sets.items()}

	def fetch(self, only, hide, urls):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for key in hide:
			del sets[key]

		maximum = 0
		results = []
		for url in urls:
			data = self.get(url, sets)
			result, width = self.lineify(url, data, sets)
			if width > maximum:
				maximum = width
			results.append(result)

		return '\n'.join(self.boxify(results, width))

	def lineify(self, url, data, sets): 
		line = 'URL: {0}'.format(url)
		width = len(line)
		lines = [line]
		for key, value in data.items():
			line = self.format(key, value)
			if len(line) > width:
				width = len(line)
			lines.append(line)
		return lines, width

	def format(self, key, value):
		key = self.reverse[key]
		if key == 'created':
			value = time.ctime(value)
		elif key == "user" and value is None:
			value = "Not public"

		return '{0}: {1}'.format(key.title(), value)

	def boxify(self, results, width):
		border = width + 2
		lines = ['┌{}┐'.format('─' * border)]
		for n, result in enumerate(results):
			for line in result:
				line = '│ {0} │'.format(line.ljust(width))
				lines.append(line)
			if n + 1 < len(results):
				lines.append('├{}┤'.format('─' * border))
		return lines + ['└{}┘'.format('─' * border)]

	def get(self, url, sets):
		self.parameters["shortUrl"] = url

		response = self.request(self.endpoints["info"])
		self.verify(response,
				   "retrieve information for {0}".format(url),
				   "info")

		response = response["data"]["info"][0]
		return {k:v for k,v in response.items() if k in sets.values()}
