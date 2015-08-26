#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import time

import bitly.link

from command import Command

def echo(*args):
	click.echo(History().fetch(*args))

class History(Command):

	def __init__(self, raw=False):
		super(History, self).__init__('bitly', 'history')
		self.raw = raw
		self.link = bitly.link.Link(raw=True)
		self.seconds = {
			"minute": 60, 
			"hour": 3600, 
			"day": 86400,
			"week": 604800, 
			"month": 18446400
		}

	def fetch(self, last, ranges, forever, limit, expanded, both, pretty):
		self.parameters['limit'] = limit

		result = self.forever(expanded, both, pretty) if forever else []
		result += self.ranges(set(ranges), expanded, both, pretty)
		result += self.last(set(last), expanded, both, pretty)

		# Remove last empty line
		result = result[:-1]

		if not pretty:
			return '\n'.join(result)
		return result if self.raw else self.boxify([result])

	def forever(self, expanded, both, pretty):
		lines = []
		for url in self.get({}):
			line = self.lineify(url, expanded, both, pretty)
			lines += [line, '']

		return ['Since forever:'] + lines if pretty else lines

	def ranges(self, ranges, expanded, both, pretty):
		lines = []
		for timespan in ranges:
			before = timespan[:2]
			after = timespan[2:]
			if pretty:
				header = 'Between {0} {1}'.format(before[0], before[1])
				header +=' and {0} {1} ago:'.format(after[0], after[1])
				lines.append(header)
			parameters = self.set_time(after, before)
			for url in self.get(parameters):
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)

		return lines

	def last(self, last, expanded, both, pretty):
		lines = []
		for timespan in last:
			if pretty:
				header = 'Last {0} {1}:'.format(timespan[0], timespan[1])
				lines.append(header)
			parameters = self.set_time(timespan)
			for url in self.get(parameters):
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)

		return lines

	def set_time(self, after=None, before=None):
		if before:
			before = self.timestamp(before)
		self.parameters['created_before'] = before
		self.parameters['created_after'] = self.timestamp(after)

	def timestamp(self, timespan):
		span = timespan[0]
		unit = timespan[1]
		if unit.endswith('s'):
			unit = unit[:-1]
		offset = span * self.seconds[unit]
		return time.time() - offset

	def lineify(self, url, expanded, both, pretty):
		if not pretty and both:
			expanded = self.link.get_long(url)
			return ' - {0} => {1}'.format(url, expanded)
		if expanded:
			url = self.link.get_long(url)
		return '- {0}'.format(url) if pretty else url

	def get(self, parameters):
		response = self.request(self.endpoints['history'], parameters)
		self.verify(response, 'retrieve history')

		return [i['link'] for i in response['data']['link_history']]
