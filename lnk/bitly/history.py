#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import ecstasy
import time

import beauty
import bitly.link

from bitly.command import Command

def echo(*args):
	click.echo(History().fetch(*args))

class History(Command):

	def __init__(self, raw=False):
		super(History, self).__init__('history')
		self.raw = raw
		self.link = bitly.link.Link(raw=True)
		self.seconds = {
			"minute": 60, 
			"hour": 3600, 
			"day": 86400,
			"week": 604800, 
			"month": 18446400,
			"year": 221356800
		}

	def fetch(self, last, ranges, forever, limit, expanded, both, pretty):
		self.parameters['limit'] = limit

		result = []
		if forever:
			result += self.forever(expanded, both, pretty)
		if ranges:
			result += self.ranges(set(ranges), expanded, both, pretty)
		if last:
			result += self.last(set(last), expanded, both, pretty)

		# Remove last empty line
		if pretty:
			del result[-1]

		if self.raw:
			return result
		return beauty.boxify([result]) if pretty else '\n'.join(result)

	def forever(self, expanded, both, pretty):
		lines = []
		for url in self.request():
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return ['Since forever:'] + lines + [''] if pretty else lines

	def ranges(self, ranges, expanded, both, pretty):
		lines = []
		for timespan in ranges:
			before = timespan[:2]
			after = timespan[2:]
			if pretty:
				header = 'Between {0} {1}'.format(before[0], before[1])
				header += ' and {0} {1} ago:'.format(after[0], after[1])
				lines.append(header)
			parameters = self.set_time(after, before)
			for url in self.request(parameters):
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)

		return lines + [''] if pretty else lines

	def last(self, last, expanded, both, pretty):
		lines = []
		for timespan in last:
			if pretty:
				header = 'Last {0} {1}:'.format(timespan[0], timespan[1])
				lines.append(header)
			parameters = self.set_time(timespan)
			for url in self.request(parameters):
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)

		return lines + [''] if pretty else lines

	def set_time(self, after=None, before=None, base=None):
		if before:
			before = self.timestamp(before, base)
		self.parameters['created_before'] = before
		self.parameters['created_after'] = self.timestamp(after, base)

	def timestamp(self, timespan, base=None):
		span = timespan[0]
		unit = timespan[1]
		if unit.endswith('s'):
			unit = unit[:-1]
		offset = span * self.seconds[unit]
		base = base or time.time()

		return base - offset

	def lineify(self, url, expanded, both, pretty):
		if both:
			expanded = self.link.get_long(url)
			url = '{0} => {1}'.format(url, expanded)
		elif expanded:
			url = self.link.get_long(url)

		if pretty:
			url = self.list_item.format(url)

		return url

	def request(self, parameters=None):
		response = self.get(self.endpoints['history'], parameters)
		response = self.verify(response, 'retrieve history')

		return [i['link'] for i in response['link_history']]
