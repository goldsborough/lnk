#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Link-history-retrieval for the goo.gl client."""

from __future__ import unicode_literals

import apiclient.discovery
import click
import ecstasy
import warnings

from collections import namedtuple
from datetime import datetime, timedelta

import beauty
import config
import errors

from googl.command import Command

warnings.filterwarnings('ignore', module=r'ecstasy\.parser')

def echo(*args):
	click.echo(History().fetch(*args))

class History(Command):

	"""
	Class to retrieve goo.gl link history for a user.

	The sole purpose of this class is to fetch and return a list of
	urls the user has shortened using goo.gl in the past. This list
	may, of course, be properly prettified if necessary. A nice feature
	is that if the history is fetched with the 'plain' flag set to true
	its output can be piped into other lnk commands, such as 'stat' or 'info'.

	Attributes:
		raw (bool): Whether to prettify the output or
					return it raw, for internal use.
		delta (dict): A mapping between string representations of time
						and equivalent datetime.timedelta objects.
	"""

	Url = namedtuple('Url', ['short', 'long', 'created'])

	def __init__(self, raw=False):
		super(History, self).__init__('history')
		self.raw = raw
		self.delta = {
			"minute": timedelta(minutes=1), 
			"hour": timedelta(hours=1), 
			"day": timedelta(days=1),
			"week": timedelta(weeks=1), 
			"month": timedelta(weeks=30.4368),
			"year": timedelta(days=365.242)
		}

	def fetch(self, last, ranges, forever, limit, expanded, both, pretty):
		data = self.request()
		urls = self.process(data)

		result = []
		if forever:
			result += self.forever(urls, limit, expanded, both, pretty)
		if ranges:
			result += self.ranges(urls, set(ranges), limit, expanded, both, pretty)
		if last:
			result += self.last(urls, set(last), limit, expanded, both, pretty)

		# Remove last empty line
		if pretty:
			del result[-1]

		if self.raw:
			return result
		return beauty.boxify([result]) if pretty else '\n'.join(result)

	def forever(self, urls, limit, expanded, both, pretty):
		lines = []
		for n, url in enumerate(urls):
			if n == limit:
				break
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return ['Since forever:'] + lines + [''] if pretty else lines

	def ranges(self, urls, ranges, limit, expanded, both, pretty):
		lines = []
		for timespan in ranges:
			begin, end = self.get_boundaries(timespan)
			filtered = self.filter(urls, begin, end)
			if pretty:
				header = self.ranges_header(timespan, filtered)
				lines.append(header)
			lines += self.listify(filtered, limit, expanded, both, pretty)

		return lines + [''] if pretty else lines

	def last(self, urls, last, limit, expanded, both, pretty):
		lines = []
		for timespan in last:
			begin = self.get_date(timespan)
			filtered = self.filter(urls, begin, datetime.now())
			if pretty:
				header = self.last_header(timespan, filtered)
				lines.append(header)
			lines += self.listify(filtered, limit, expanded, both, pretty)

		return lines + [''] if pretty else lines

	def ranges_header(self, timespan, filtered):
		first_unit = ''
		if timespan[1] != timespan[3]:
			first_unit = '{0} '.format(timespan[1])
		header = 'Between {0} {1}'.format(timespan[0], first_unit)
		header += 'and {0} {1} ago:'.format(timespan[2], timespan[3])

		return header if filtered else header + ' None'

	def last_header(self, timespan, filtered):
		span = '{0} '.format(timespan[0]) if timespan[0] > 1 else ''
		header = 'Last {0}{1}:'.format(span, timespan[1])

		return header if filtered else header + ' None'

	def get_date(self, time_range, base=None):
		span = time_range[0]
		unit = time_range[1]
		if unit.endswith('s'):
			unit = unit[:-1]
		offset = span * self.delta[unit]
		base = base or datetime.now()

		return base - offset

	def get_boundaries(self, timespan, base=None):
		begin = self.get_date(timespan[:2], base)
		end = self.get_date(timespan[2:], base)
		if end < begin:
			raise errors.UsageError("Illegal time range 'between {0} "
									"and {1} and {2} {3} ago' (start must"
									"precede end)"
									"!".format(timespan[0], timespan[1],
											   timespan[2], timespan[3]))
		return begin, end

	def request(self):
		api = self.get_api()
		request = api.list()
		response = self.execute(request, 'retrieve history')

		return response

	def listify(self, urls, limit, expanded, both, pretty):
		lines = []
		for n, url in enumerate(urls):
			if n == limit:
				break
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return lines

	def lineify(self, url, expanded, both, pretty):
		if both:
			line = '{0} => {1}'.format(url.short, url.long)
		elif expanded:
			line = url.long
		else:
			line = url.short

		if pretty:
			marked = self.list_item.format(line)
			line = ecstasy.beautify(marked, ecstasy.Color.Red)

		return line

	@staticmethod
	def filter(urls, begin, end):
		filtered = []
		for url in urls:
			if url.created >= begin and url.created <= end:
				filtered.append(url)

		return filtered

	@staticmethod
	def process(data):
		urls = []
		for item in data['items']:
			relevant = item['created'].split('.')[0]
			created = datetime.strptime(relevant, '%Y-%m-%dT%H:%M:%S')
			url = History.Url(item['id'], item['longUrl'], created)
			urls.append(url)

		return urls
