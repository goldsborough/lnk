#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Link-history-retrieval for the bit.ly client."""

from __future__ import unicode_literals

import click
import time

import lnk.beauty
import lnk.bitly.link

from lnk.bitly.command import Command

def echo(*args):
	"""
	Executes a history command and echoes its output.

	Arguments:
		args (variadic): The arguments to pass to a
						 History instance's fetch() method.
	"""
	click.echo(History().fetch(*args))

class History(Command):
	"""
	Class to retrieve bit.ly link history for a user.

	The sole purpose of this class is to fetch and return a list of
	urls the user has shortened using bit.ly in the past. This list
	may, of course, be properly prettified if necessary. A nice feature
	is that if the history is fetched with the 'plain' flag set to true
	its output can be piped into other lnk commands, such as 'stat' or 'info'.

	Attributes:
		raw (bool): Whether to prettify the output or
					return it raw, for internal use.
		link (bit.ly.link.Link): A link instance to expand short links.
		seconds (dict): A mapping between string representations of time
						and equivalent numbers of seconds for each unit.
	"""
	def __init__(self, raw=False):
		super(History, self).__init__('history')
		self.raw = raw
		self.link = lnk.bitly.link.Link(raw=True)
		self.seconds = {
			'minute': 60, 
			'hour': 3600, 
			'day': 86400,
			'week': 604800, 
			'month': 2629740,
			'year': 31556900
		}

	def fetch(self, last, ranges, forever, limit, expanded, both, pretty):
		"""
		Fetches the link history.

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
		return lnk.beauty.boxify([result]) if pretty else '\n'.join(result)

	def forever(self, expanded, both, pretty):
		"""
		Fetches and formats history since forever.

		Arguments:
			expanded (bool): Whether to show exapanded or short links.
			both (bool): Whether to show both expanded and short links.
			pretty (bool): Whether to prettify the output.

		Returns:
			A plain list of lines ready if pretty is false, else the
			same list of lines with a header ('Since forever:') plus
			an empty line for padding.
		"""
		lines = []
		for url in self.request():
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return ['Since forever:'] + lines + [''] if pretty else lines

	def ranges(self, ranges, expanded, both, pretty):
		"""
		Fetches and formats history for certain time ranges.

		Arguments:
			ranges (tuple): The time-ranges of schema (span1, unit1, span2, unit2).
			expanded (bool): Whether to show expanded or short links.
			both (bool): Whether to show both expanded and short links.
			pretty (bool): Whether to prettify the output.

		Returns:
			A plain list of lines ready if pretty is false, else the
			same list of lines with a header (e.g. 'Between 7 months and
			5 days ago:'), plus an empty line for padding.
		"""
		lines = []
		for time_point in ranges:
			before = time_point[2:]
			after = time_point[:2]
			parameters = self.parse_time(after, before)
			urls = self.request(parameters)
			if pretty:
				header = self.ranges_header(after, before, urls)
				lines.append(header)
			for url in urls:
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)
			if pretty:
				lines.append('')

		return lines

	def last(self, last, expanded, both, pretty):
		"""
		Fetches and formats history after a given time-point.

		Arguments:
			last (tuple): The open-ended time-ranges of schema (span, unit).
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
			parameters = self.parse_time(time_point)
			urls = self.request(parameters)
			if pretty:
				header = self.last_header(time_point, urls)
				lines.append(header)
			for url in urls:
				line = self.lineify(url, expanded, both, pretty)
				lines.append(line)
			if pretty:
				lines.append('')

		return lines

	def ranges_header(self, after, before, urls):
		"""
		Returns a header for a time-range.

		Arguments:
			after (tuple): The lower-bound time-point.
			before (tuple): The upper-bound time-point.
			urls (list|tuple): The urls, to check if empty.

		Returns:
			A header of the schema 'Between <span1> [<unit1>] and <span2>
			<unit2>', where <unit1> is only included if it not equal to
			<unit2>, i.e. 'Between 3 days and 2 days ago' is transformed to
			'Between 3 and 2 days ago'. If the urls are empty, ' None' is
			appended to the header.
		"""
		first_unit = ''
		if before[1] != after[1]:
			first_unit = '{0} '.format(after[1])
		header = 'Between {0} {1}'.format(after[0], first_unit)
		header += 'and {0} {1} ago:'.format(before[0], before[1])

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

	def parse_time(self, after=None, before=None, base=None):
		"""
		Parses one or two time-points for an HTTP request.

		The time-range can have a lower-bound and an upper-bound,
		but does not need to have either.

		Arguments:
			after (tuple): The lower-bound time-point.
			before (tuple): The upper-bound time-point.

		Returns:
			Parameters ready for an HTTP request to the bit.ly API,
			as a dictionary (dict).
		"""
		if before:
			before = self.timestamp(before, base)
		parameters = {
			'created_before': before,
			'created_after': self.timestamp(after, base)
		}

		return parameters

	def timestamp(self, time_point, base=None):
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
		offset = span * self.seconds[unit]
		base = base or time.time()

		return int(base - offset)

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
			expanded = self.link.get_long(url)
			url = '{0} => {1}'.format(url, expanded)
		elif expanded:
			url = self.link.get_long(url)

		if pretty:
			url = self.list_item.format(url)

		return url

	def request(self, parameters=None):
		"""
		Requests the link-history from the bit.ly API.

		Arguments:
			parameters (dict): Parameters to pass along with the request 
							   (like created_after/created_before).

		Returns:
			A list of links.
		"""
		response = self.get(self.endpoints['history'], parameters)
		response = self.verify(response, 'retrieve history')

		return [i['link'] for i in response['link_history']]
