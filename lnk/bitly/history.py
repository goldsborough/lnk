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

	def fetch(self, last, ranges, forever, limit, expanded, both, listed):
		self.parameters['limit'] = limit

		result = self.forever(expanded, both, listed) if forever else []
		result += self.ranges(ranges, expanded, both, listed)
		result += self.last(last, expanded, both, listed)

		# Remove last empty line
		result = result[:-1]

		if listed:
			return '\n'.join(result)
		return result if self.raw else self.boxify([result])

	def forever(self, expanded, both, listed):
		urls = self.lineify(expanded, both, listed)
		return urls if listed else ['Since forever:'] + urls

	def ranges(self, ranges, expanded, both, listed):
		lines = []
		for timespan in ranges:
			before = timespan[:2]
			after = timespan[2:]

			if not listed:
				header = 'Between {0} {1}'.format(before[0], before[1])
				header +=' and {0} {1} ago:'.format(after[0], after[1])
				lines.append(header)

			self.set_time(after, before)
			lines += self.lineify(expanded, both, listed)

		return lines

	def last(self, last, expanded, both, listed):
		lines = []
		for timespan in last:
			if not listed:
				header = 'Last {0} {1}:'.format(timespan[0], timespan[1])
				lines.append(header)
			self.set_time(timespan)
			lines += self.lineify(expanded, both, listed)
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

	def lineify(self, expanded, both, listed):
		lines = []
		for url in self.get():
			if both or expanded is None:
				line = self.link.get_long(url)
				if not listed:
					line = ' - {0} => {1}'.format(url, line)
				lines.append(line)
			else:
				if expanded:
					url = self.link.get_long(url)
				if not listed:
					url = '- {0}'.format(url)
				lines.append(url)
		return lines + ['']

	def get(self):
		response = self.request(self.endpoints['history'])
		self.verify(response, 'retrieve history')

		return [i['link'] for i in response['data']['link_history']]
