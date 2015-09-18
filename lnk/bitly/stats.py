#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Statistics and metrics retrieval for bitlinks."""

from __future__ import unicode_literals

import click
import ecstasy
import time

from collections import namedtuple

import lnk.abstract
import lnk.beauty
import lnk.bitly.info
import lnk.countries
import lnk.errors

from lnk.bitly.command import Command

def echo(*args):
	"""
	Executes a stats command and echoes its output.

	Arguments:
		args (variadic): The arguments to pass to a
						 Stats instance's fetch() method.
	"""
	click.echo(Stats().fetch(*args))

class Stats(Command):
	"""
	Class to retrieve statistics and info for one or more bitlinks.

	The statistics for a link include its referrers (i.e. from where the link
	was opened), the countries from where the link was opened and of course the
	number of clicks. These statistics can be retrieved 'since-forever', but
	also for specific (possibly open-ended) time-ranges, such as for 'the last
	5 months' or 'between 4 days and 2 minute ago'. Additionally, these
	statistics can be paired with information about each link, retrieved from
	the 'info' command, thereby making the stats command the ultimate
	destination for link statistics *and* information. Output may, as always,
	be in raw format for internal use or in a pretty box. Multiple URLs are
	fully supported.

	Attributes:
		raw (bool): Whether to return the output in raw format for internal use,
					or in a pretty string-representation for outside-display.
		info (lnk.bitly.info.Info): A lnk.bitly.info.Info instance to retrieve
							    addittional information for a bitlink.
	"""

	Timespan = namedtuple('Timespan', ['span', 'unit'])

	def __init__(self, raw=False):
		super(Stats, self).__init__('stats')

		self.raw = raw
		self.info = lnk.bitly.info.Info(raw=True)
		self.parameters['timezone'] = time.tzname[0]

	def fetch(self, only, hide, times, forever, limit, add_info, full, urls):
		"""
		Fetches statistics for one or more URLs.

		Arguments:
			only (tuple): A tuple of strings representing the sets to include
						  in the response ('only' these will be included).
			hide (tuple): A tuple of strings representing the sets to hide
						  from the response (either from all possible sets
						  if only is empty, or else from those selected).
			times (tuple): A tuple of tuples of the schema (<span>, <unit>),
						   representing the timespans for which to fetch
						   statistics.
			forever (bool): Whether to include the statistics 'since forever'.
			limit (int): A limit on the number of items fetched per timespan.
			add_info (bool): Whether or not to add additional information for
							 each link.
			full (bool): Whether to show full country names, or short ISO
						 abbreviations.
			urls (tuple): A tuple of urls to fetch statistics for.

		Returns:
			A plain list of the raw lines if the 'raw' attribute is True,
			else a boxified, pretty string.
		"""
		self.parameters['limit'] = limit

		sets = lnk.abstract.filter_sets(self.sets, only, hide)
		timespans = self.get_timespans(times, forever)
		info = []
		if add_info:
			info = self.info.fetch([], [], False, urls)
			if not info:
				raise lnk.errors.InternalError('Could not fetch additional info.')

		results = []
		for n, url in enumerate(urls):
			header = info[n] if add_info else ['URL: {0}'.format(url)]
			data = self.get_stats(url, timespans, sets)
			lines = self.lineify(data, full)

			results.append(header + lines)

		return results if self.raw else lnk.beauty.boxify(results)

	def get_stats(self, url, timespans, sets):
		"""
		Retrieves the statistics for a single url.

		The statistics returned are for all timespans supplied, filtered
		according to the sets of statistics wanted.

		Note:
			This method works with threads. For each category and each
			timespan, a new request must be made. Each request is made
			in a separate thread.

		Arguments:
			url (str): The relevant URL to fetch statistics for.
			timespans (tuple): A tuple of tuples of the schema (<span>, <unit>),
							   representing the timespans for which to fetch
							   statistics.
			sets (tuple): The sets of statistics wanted in the response
						 (others are discarded).

		Returns:
			A single 'result', which is a dictionary where the keys are
			the sets (categories) and the values a list of the statistics
			that were fetched for each timespan. Each item in this list
			is in turn a dictionary with one key/value pair for the timespan
			and another for the data retrieved in that category,
			for that timespan. This data is either an integer for the 'clicks'
			category, or a list representing each individual data-point that
			could be fetched. Each of those data-points has a 'clicks' key
			whose value is an integer representing the clicks for that
			data-point. A data-point also has another key, which depends on the
			category, e.g. 'country' for the 'countries' category.
		"""
		parameters = {'link': url}
		result = {}
		threads = []
		for endpoint in sets:
			result[endpoint] = []
			for timespan in timespans:

				parameters['unit'] = timespan.unit

				if timespan.unit.endswith('s'):
					# Get rid of the plural s in e.g. 'weeks'
					parameters['unit'] = timespan.unit[:-1]

				parameters['units'] = timespan.span

				self.queue.put((url, endpoint, timespan, parameters))
				threads.append(self.new_thread(self.request, result))
		self.join(threads)

		return result

	def request(self, results):
		"""
		Requests statistics for a given configuration.

		The URL, endpoint (set/category) and timespan are all fetched from
		a queue, because this method is always run in a separate thread for
		each configuration of the above parameters. The dictionary to which
		to insert the data must be passed as an argument. The data is
		inserted in a thread-safe, locked way.

		Arguments:
			results (dict): The results dictionary for the URL, to which to
							insert the retrieved statistics.
		"""
		url, endpoint, timespan, parameters = self.queue.get()

		response = self.get(self.endpoints[endpoint], parameters)
		what = "retrieve {0} for '{1}'".format(endpoint, url)
		response = self.verify(response, what)

		# For 'clicks' the key has a different name than the endpoint
		e = endpoint if endpoint != 'clicks' else 'link_clicks'
		data = {'timespan': timespan, 'data': response[e]}

		with self.lock:
			results[endpoint].append(data)

	def get_timespans(self, times, forever):
		"""
		Parses the timespans passed to fetch and returns Timespan objects.

		The timespans passed to the command-line interface and ultimately
		to the fetch() method are of the schema '(<span>, <unit>)'. These
		are parsed into Stats.Timespan objects. Parsing handles cases such
		as where the unit is 'year'. Bitly cannot handle 'year' as a unit,
		so the timespan must be converted into weeks. Also the 'forever' flag
		is handled here. Moreover, this method retrieves the default timespan
		from the configuration file if no timespans were passed to the method
		(and the command on the CLI).

		Arguments:
			times (tuple): The timespans of the schema '(<span>, <unit>)'.
			forever (bool): Whether to include the 'since forever' timespan.

		Returns:
			A list of Stats.Timespan objects.
		"""
		timespans = set()
		if forever:
			# -1 = since forever (unit could be any)
			timespans.add(Stats.Timespan(-1, 'day'))
		if times:
			for span, unit in times:
				if 'year' in unit:
					span *= 12
					unit = 'months'
				timespans.add(Stats.Timespan(span, unit))
		elif not forever:
			# Get the default from the settings
			unit = self.settings['unit']
			span = self.settings['span']
			if not unit or not span:
				raise lnk.errors.InternalError('Default timespan is invalid!')
			if unit == 'forever':
				timespans.add(Stats.Timespan(-1, 'day'))
			elif 'year' in unit:
				timespans.add(Stats.Timespan(span * 12, 'months'))
			else:
				timespans.add(Stats.Timespan(span, unit))

		return timespans

	def lineify(self, data, full):
		"""
		Turns the data retrieved for a link into a list of lines.

		Each category has a header containing a string-representation of
		the category. For each timespan of a given category, a list is
		created if the category holds multiple data-points. Lines containing
		timespans and data-points are formatted into list-items using ecstasy.

		Arguments:
			data (dictionary): The data (statistics) to lineify. This data
							   should hold key/value pairs where the keys
							   are the sets/categories of data and the
							   values lists of dictionaries for each timespan.
			full (bool): Whether to show full country names or short
						 ISO abbreviations (e.g. 'Germany' or 'DE').
		Returns:
			A list of lines, ready for output.
		"""
		lines = []
		for category, items in data.items():
			lines.append('{0}:'.format(category.title()))
			lines += self.listify(category, items, full)

		return lines

	def listify(self, category, data, full):
		"""
		Formats data with multiple data-points into a pretty list.

		Arguments:
			category (str): The category to which the data belongs
							(e.g. referrers).
			data (dict): The actual data, as a dictionary.
			full (bool): Whether to show full country names or short
						 ISO abbreviations (e.g. 'Germany' or 'DE').
		Returns:
			A list of lines, ready for output.
		"""
		lines = []
		for result in data:
			timespan = result['timespan']
			items = result['data']
			header = self.get_header(timespan.span, timespan.unit)
			lines.append(header)
			if not items:
				lines[-1] += ' None'
			elif isinstance(items, list):
				for item in items:
					clicks = item.pop('clicks')
					key = item.values()[0]
					line = self.format(category, key, clicks, full)
					lines.append(line)
			else:
				# for clicks
				lines[-1] += ' {0}'.format(items)

		return lines

	def get_header(self, span, unit):
		"""
		Handles formatting of a timespan header.

		This method handles cases such as the 'since forever' timespan, as
		well as the issue with years (years have to be converted to months
		for bitly).

		Arguments:
			span (int): The span of the timespan (e.g. *4* months).
			unit (str): The unit of the timespan (e.g.. 4 *months*).

		Returns:
			A pretty list-item containing the timespan information.
		"""
		if span == -1:
			header = 'Since forever:'
		else:
			# Do this only for year because years have to be
			# converted to months before requesting stats from
			# the API, but it looks weird to the user if he
			# wanted years and got an equivalent number of months
			if unit == 'months' and span % 12 == 0:
				span /= 12
				unit = 'years' if span > 1 else 'year'
			span = '{0} '.format(span) if span > 1 else ''
			header = 'Last {0}{1}:'.format(span, unit)

		return self.list_item.format(header)

	@staticmethod
	def format(category, key, value, full):
		"""
		Formats a key/value pair for output.

		Handles special cases such as country-name expansion (the API returns
		them as ISO abbreviations, e.g. 'DE', but often the full name,
		e.g. 'Germany', is really wanted)

		Arguments:
			category (str): The category of the data.
			key (str): The key of the data-point.
			value (str): The value of the data-point.
			full (bool): Whether to show full country names or short
						 ISO abbreviations (e.g. 'Germany' or 'DE').

		Returns:
			A pretty list-item.
		"""
		if category == 'countries':
			if key == 'None':
				key = 'Other'
		 	elif full:
				key = lnk.countries.names[key]
		elif key == 'direct':
			key = key.title()
		line = '   <-> {0}: {1}'.format(key, value)
		pretty = ecstasy.beautify(line, ecstasy.Color.Yellow)

		return pretty
