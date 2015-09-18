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

import lnk.beauty
import lnk.config
import lnk.errors

from lnk.googl.command import Command

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
		Url (namedtuple): Class-attribute namedtuple to represent a link
						  with a short, long/expanded url and a creation
						  date.

	Note:
		The datetime.timedelta objects store time-offsets as floating-point
		values (e.g. 1 year = 365.242199 days) to account for time-weirdness
		such as shift-years, but they will nevertheless not be absolutely
		precise, but good enough.
	"""

	Url = namedtuple('Url', ['short', 'long', 'created'])

	def __init__(self, raw=False):
		super(History, self).__init__('history')
		self.raw = raw
		self.delta = {
			'minute': timedelta(minutes=1), 
			'hour': timedelta(hours=1), 
			'day': timedelta(days=1),
			'week': timedelta(weeks=1), 
			'month': timedelta(days=30.4368),
			'year': timedelta(days=365.242199)
		}

	def fetch(self, last, ranges, forever, limit, expanded, both, pretty):
		"""
		Fetches the link history and returns a string for output.

		Arguments:
			last (tuple): A tuple of time_points to retrieve history for, without
						  an upper bound (i.e. all links after a given time_point,
						  up to now).
			ranges (tuple): A tuple of time_point-ranges to retrieve history for
							(with a lowe and upper bound).
			forever (bool): Whether or not to include data for all
							time_points (since forever).
			limit (int): A limit on the number of datapoints fetched per time_point.
			expanded (bool): Whether or not to show expanded rather
							 than short links.
			both (bool): Whether or not to show both short and expanded links
						 (takes precedence over 'expanded').
			pretty (bool): Whether or not to prettify the output.

		Returns:
			A plain list of the raw lines if the 'raw' attribute is true,
			else a boxified, pretty string if the pretty flag is set,
			else the same plain list as for the first case, but joined to
			a string.
		"""
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
		return lnk.beauty.boxify([result]) if pretty else '\n'.join(result)

	def forever(self, urls, limit, expanded, both, pretty):
		"""
		Formats history for all possible time-ranges.

		Arguments:
			urls (list|tuple): The original/full list of urls.
			limit (int): A limit to the number of links to pick.
			expanded (bool): Whether to show expanded or short links.
			both (bool): Whether to show both expanded and short links.
			pretty (bool): Whether to prettify the output.

		Returns:
			A plain list of lines ready if pretty is false, else the
			same list of lines with a header ('Since forever:') plus
			an empty line for padding.
		"""
		lines = []
		for n, url in enumerate(urls):
			if n == limit:
				break
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return ['Since forever:'] + lines + [''] if pretty else lines

	def ranges(self, urls, ranges, limit, expanded, both, pretty):
		"""
		Formats and filters history for certain time ranges.

		Arguments:
			urls (list|tuple): The original/full list of urls.
			ranges (tuple): The time-ranges of schema (span1, unit1, span2, unit2).
			limit (int): A limit to the number of links to pick for each time-range.
			expanded (bool): Whether to show expanded or short links.
			both (bool): Whether to show both expanded and short links.
			pretty (bool): Whether to prettify the output.

		Returns:
			A plain list of lines ready if pretty is false, else the
			same list of lines with a header (e.g. 'Between 7 months and
			5 days ago:'), plus an empty line for padding.
		"""
		lines = []
		for time_range in ranges:
			begin, end = self.get_boundaries(time_range)
			filtered = self.filter(urls, begin, end)
			if pretty:
				header = self.ranges_header(time_range, filtered)
				lines.append(header)
			lines += self.listify(filtered, limit, expanded, both, pretty)
			if pretty:
				lines.append('')

		return lines

	def last(self, urls, last, limit, expanded, both, pretty):
		"""
		Fetches and formats history after a given time-point.

		Arguments:
			urls (list|tuple): The original/full list of urls.
			last (tuple): The open-ended time-ranges of schema (span, unit).
			limit (int): A limit to the number of links to pick for each
						 time-range.
			expanded (bool): Whether to show exapanded or short links.
			both (bool): Whether to show both expanded and short links.
			pretty (bool): Whether to prettify the output.

		Returns:
			A plain list of lines ready if pretty is false, else the
			same list of lines with a header (e.g. 'Last 4 weeks:'),
			plus an empty line for padding.
		"""
		lines = []
		for time_point in last:
			begin = self.get_date(time_point)
			filtered = self.filter(urls, begin, datetime.now())
			if pretty:
				header = self.last_header(time_point, filtered)
				lines.append(header)
			lines += self.listify(filtered, limit, expanded, both, pretty)
			if pretty:
				lines.append('')

		return lines

	def ranges_header(self, time_range, urls):
		"""
		Returns a header for a time-range.

		Arguments:
			time_range (tuple): The time-range following the
								schema (span1, unit1, span2, unit2).
			urls (list|tuple): The urls, to check if empty.

		Returns:
			A header of the schema 'Between <span1> [<unit1>] and <span2>
			<unit2>', where <unit1> is only included if it not equal to
			<unit2>, i.e. 'Between 3 days and 2 days ago' is transformed to
			'Between 3 and 2 days ago'. If the urls are empty, ' None' is
			appended to the header.
		"""
		first_unit = ''
		if time_range[1] != time_range[3]:
			first_unit = '{0} '.format(time_range[1])
		header = 'Between {0} {1}'.format(time_range[0], first_unit)
		header += 'and {0} {1} ago:'.format(time_range[2], time_range[3])

		return header if urls else header + ' None'

	def last_header(self, time_point, urls):
		"""
		Returns a header for an open-ended time-range.

		Arguments:
			time_point (tuple): The lower-bound time-point.
			urls (list|tuple): The urls, to check if empty.

		Returns:
			A header of the schema 'Last [<span>] <unit>'. The span is
			only shown if it is greater 1, such that 'Last 1 day' will be
			displayed as 'Last day'. If the urls are empty, ' None' is 
			appended to the header.
		"""
		span = '{0} '.format(time_point[0]) if time_point[0] > 1 else ''
		header = 'Last {0}{1}:'.format(span, time_point[1])

		return header if urls else header + ' None'

	def get_date(self, time_point, base=None):
		"""
		Returns a UNIX timestamp for a given time-point.

		The timestamp is base timestamp (either supplied to the function
		call or time.time()) minus the time_point, parsed into seconds.

		Arguments:
			time_point (tuple): A time_point tuple of the schema (span, unit).
			base (int): The base time-value from which to subtract the offset,
						defaults to time.time().

		Returns:
			A UNIX timestamp, in seconds, as an integer (!).
		"""
		span = time_point[0]
		unit = time_point[1]
		if unit.endswith('s'):
			unit = unit[:-1]
		offset = span * self.delta[unit]
		base = base or datetime.now()

		return base - offset

	def get_boundaries(self, time_range, base=None):
		"""
		Gets a lower and upper-bound timestamp for a given time_range.

		Also checks whether the starting point is before the end point,
		and throws a UsageError if not (the user passed the range in the
		wrong format, e.g. -r 5 day 7 weeks).

		Arguments:
			time_range (tuple): The time-range following the
								schema (span1, unit1, span2, unit2).
			base (int): The base timestamp to pass to get_date().

		Raises:
			errors.UsageError: if the starting point is after the end point.

		Returns:
			The begin and end timestamps (datetime objects).

		"""
		begin = self.get_date(time_range[:2], base)
		end = self.get_date(time_range[2:], base)
		if end < begin:
			what = "Illegal time range 'between {0} and {1} and {2} {3} "\
				   "ago' (start must precede end)"\
				   '!'.format(time_range[0], time_range[1],
							  time_range[2], time_range[3])
			raise lnk.errors.UsageError(what)
		return begin, end

	def request(self):
		"""
		Requests the link-history from the bit.ly API.

		Returns:
			A list of links.
		"""
		api = self.get_api()

		data = []
		response = {'nextPageToken': None}
		while 'nextPageToken' in response:
			request = api.list(start_token=response['nextPageToken'])
			response = self.execute(request, 'retrieve history')
			data += response['items']

		return data

	def listify(self, urls, limit, expanded, both, pretty):
		"""
		Returns a list of lines for a list of urls.

		Also performs limiting according to the 'limit' parameter.

		Arguments:
			urls (tuple|list): The urls to listify.
			limit (int): A limit to the number of urls to listify.
			expanded (bool): Whether to show expanded or short links.
			both (bool): Whether to show both short and expanded links.
			pretty (bool): Whether to format the output.

		Returns:
			A list of lines, ready for input. The length of the returned
			list will always be at most equal to the limit, if the limit
			is not None.
		"""
		lines = []
		for n, url in enumerate(urls):
			if n == limit:
				break
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return lines

	def lineify(self, url, expanded, both, pretty):
		"""
		Returns an output-ready line for a given url.

		The line may include only the short url, only the long/expanded
		url or both, depending on the parameters passed.

		Arguments:
			url (str): The short url.
			expanded (bool): Whether or not to show the expanded link.
			both (bool): Whether or not to show both the short and the
						 expanded link (takes precedence over 'expanded').
			pretty (bool): Whether or not to make the output pretty.

		Returns:
			The short url if neither 'expanded' nor 'both' is set,
			both the short and the expanded url, in the schema '<short> =>
			<expanded>' if 'both' is set, else only the expanded link if
			'expanded' is set. If 'pretty' is True, the line is returned
			in a formatted fashion (with color), else in plain format.
		"""
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
		"""
		Filters a list of urls according to a lower and upper-bound time-point.

		Arguments:
			urls (list|tuple): A list/tuple of urls to filter.
			begin (int): The lower-bound datetime object (all links mus be
						 created at or after this point in time).
			end (int): The upper-bound datetime object (all links mus be
						 created at or before this point in time).

		Returns:
			A list of filtered urls.

		Note:
			The passed list of urls is not modified directly, i.e.
			the filtered list is a new list.
		"""
		filtered = []
		for url in urls:
			if url.created >= begin and url.created <= end:
				filtered.append(url)

		return filtered

	@staticmethod
	def process(data):
		"""
		Processes data retrieved from the API.

		Given a url, this method returns a History.Url object constisting
		of the short url, the expanded url and a datetime.datetime object
		for its date of creation.

		Arguments:
			data (list): The data from the HTTP request sent in the
						 request() method.

		Returns:
			A list of History.Url objects.
		"""
		urls = []
		for item in data:
			relevant = item['created'].split('.')[0]
			created = datetime.strptime(relevant, '%Y-%m-%dT%H:%M:%S')
			url = History.Url(item['id'], item['longUrl'], created)
			urls.append(url)

		return urls
