#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Link-history-retrieval for the bitly client."""

from __future__ import unicode_literals

import click
import time

import beauty
import bitly.link

from bitly.command import Command

def echo(*args):
	click.echo(History().fetch(*args))

class History(Command):
	"""
	Class to retrieve link history for a user.

	The sole purpose of this class is to fetch and return a list of
	urls the user has shortened using bitly in the past. This list
	may, of course, be properly prettified if necessary. A nice feature
	is that if the history is fetched with the 'plain' flag set to true
	its output can be piped into other lnk commands, such as 'stat' or 'info'.
	"""

	def __init__(self, raw=False):
		"""
		
		"""
		super(History, self).__init__('history')
		self.raw = raw
		self.link = bitly.link.Link(raw=True)
		self.seconds = {
			"minute": 60, 
			"hour": 3600, 
			"day": 86400,
			"week": 604800, 
			"month": 2629740,
			"year": 31556900
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
			before = timespan[2:]
			after = timespan[:2]
			parameters = self.set_time(after, before)
			urls = self.request(parameters)
			if pretty:
				header = 'Between {0} {1}'.format(after[0], after[1])
				header += ' and {0} {1} ago:'.format(before[0], before[1])
				if not urls:
					header += ' None'
				lines.append(header)
			for url in urls:
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)

		return lines + [''] if pretty else lines

	def last(self, last, expanded, both, pretty):
		lines = []
		for timespan in last:
			parameters = self.set_time(timespan)
			urls = self.request(parameters)
			if pretty:
				span = '{0} '.format(timespan[0]) if timespan[0] > 1 else ''
				header = 'Last {0}{1}:'.format(span, timespan[1])
				if not urls:
					header += ' None'
				lines.append(header)
			for url in urls:
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)

		return lines + [''] if pretty else lines

	def set_time(self, after=None, before=None, base=None):
		if before:
			before = self.timestamp(before, base)
		parameters = {
			'created_before': before,
			'created_after': self.timestamp(after, base)
		}

		return parameters

	def timestamp(self, timespan, base=None):
		span = timespan[0]
		unit = timespan[1]
		if unit.endswith('s'):
			unit = unit[:-1]
		offset = span * self.seconds[unit]
		base = base or time.time()

		return int(base - offset)

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
