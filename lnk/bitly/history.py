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

	def fetch(self, last, ranges, forever, limit, expanded, both):
		self.parameters['limit'] = limit

		result = self.forever(expanded, both) if forever else []
		result += self.ranges(ranges, expanded, both)
		result += self.last(last, expanded, both)

		# Remove last empty line
		result = result[:-1]

		return result if self.raw else self.boxify([result])

	def forever(self, expanded, both):
		header = ['Since forever:']
		return header + self.get_list(expanded, both)

	def ranges(self, ranges, expanded, both):
		lines = []
		for timespan in ranges:
			before = timespan[:2]
			after = timespan[2:]

			header = 'Between {0} {1}'.format(before[0], before[1])
			header +=' and {0} {1} ago:'.format(after[0], after[1])
			lines.append(header)

			self.set_time(after, before)
			lines += self.get_list(expanded, both)

		return lines

	def last(self, last, expanded, both):
		lines = []
		for timespan in last:
			header = 'Last {0} {1}:'.format(timespan[0], timespan[1])
			lines.append(header)
			self.set_time(timespan)
			lines += self.get_list(expanded, both)
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

	def get_list(self, expanded, both):
		lines = []
		for url in self.get():
			if both or expanded is None:
				expanded = self.link.get_long(url)
				lines.append(' - {0} => {1}'.format(url, expanded))
			elif expanded:
				expanded = self.link.get_long(url)
				lines.append('- {0}'.format(expanded))
			else:
				lines.append('- {0}'.format(url))
		return lines

	def get(self):
		response = self.request(self.endpoints['history'])
		self.verify(response, 'retrieve history')

		return [i['link'] for i in response['data']['link_history']]
