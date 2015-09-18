#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Statistics and metrics retrieval for goo.gl."""

from __future__ import unicode_literals

import click
import ecstasy

import lnk.abstract
import lnk.beauty
import lnk.countries

from lnk.googl.command import Command

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
	Class to retrieve statistics and info for one or more goo.gl links.

	The statistics for a link include its referrers (i.e. from where the link
	was opened), the countries from where the link was opened, the browsers in
	which the link was opened, the platforms (operating systems) from which the
	link was opened and of course the number of clicks. These statistics can be
	retrieved 'since-forever', but also for specific (possibly open-ended)
	time-ranges, such as for 'the last 5 months' or 'between 4 days and 2 minute
	ago'. Additionally, these statistics can be paired with information about
	each link, retrieved from the 'info' command, thereby making the stats
	command the ultimate destination for link statistics *and* information.
	Output may, as always, be in raw format for internal use or in a pretty box.
	Multiple URLs are fully supported.

	Attributes:
		raw (bool): Whether to return the output in raw format for internal use,
					or in a pretty string-representation for outside-display.
	"""
	def __init__(self, raw=False):
		super(Stats, self).__init__('stats')
		self.raw = raw

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
		sets = lnk.abstract.filter_sets(self.sets, only, hide)
		timespans = self.get_timespans(times, forever)

		results = []
		threads = []
		for url in urls:
			self.queue.put(url)
			args = (results, sets, timespans, add_info, full, limit)
			thread = self.new_thread(self.get_stats, *args)
			threads.append(thread)
		self.join(threads)

		return results if self.raw else lnk.beauty.boxify(results)

	def get_stats(self, results, sets, timespans, add_info, full, limit):
		"""
		Retrieves the statistics for a single url.

		The statistics returned are for all timespans supplied, filtered
		according to the sets of statistics wanted.

		Arguments:
			results (list): The list of results to which to append the
							retreived data.
			sets (tuple): The sets of statistics wanted in the response
						 (others are discarded).
			timespans (tuple): A tuple of tuples of the schema (<span>, <unit>),
							   representing the timespans for which to fetch
							   statistics.
			add_info (bool): Whether to add information about each url
							 alongside statistics.
			full (bool): Whether to show full country names or short ISO
						 abbreviations.
			limit (int): A limit to the number of data-points selected for each
						 timespan.
		"""
		data = self.request(add_info)
		lines = self.lineify(data, sets, timespans, full, limit)
		with self.lock:
			results.append(lines)

	def request(self, add_info):
		"""
		Requests statistics for a given configuration.

		The url for which to retrieve statistics is fetched from the queue
		attribute (thread-safe).

		Arguments:
			add_info (bool): Whether to add information about the URL as well.

		Returns:
			The dictionary containing the retrieved data. The format of this
			dictionary is that it contains a 'URL' key, as well as all key/value
			pairs connected to information. It also contains an 'analytics' key,
			whose value are the actual statistics for the URL. These statistics
			are a dictionary where the keys are the timespans and the values
			the data for each timespan. This data is then furthermore a
			dictionary which maps the category/set names to list of data-points.
			Each data-point's key is contained in the 'id' key (e.g. the name
			of a country) and the value (always the number of clicks) is
			found with the 'count' key.

		"""
		url = self.queue.get()
		what = "get information for '{0}'".format(url)
		data = self.get(url, 'FULL', what)

		data['URL'] = url
		del data['kind']
		del data['id']
		if not add_info:
			for i in ['created', 'longUrl', 'status']:
				del data[i]

		return data

	def lineify(self, data, sets, timespans, full, limit):
		"""
		Turns the data retrieved for a link into a list of lines.

		Information about the URL is formatted and turned into header-lines
		here, the statistics are entirely parsed in the listify() method.

		Arguments:
			data (dictionary): The data (statistics) to lineify.
			sets (tuple): The names of the sets to include in the output.
			timespans (tuple): The timespans for which to include data.
			full (bool): Whether to show full country names or short
						 ISO abbreviations (e.g. 'Germany' or 'DE').
			limit (int): A limit on the number of data-points retrieved per
						 timespan.
		Returns:
			A list of lines, ready for output.
		"""
		stats = data.pop('analytics')
		statistics = self.listify(stats, sets, timespans, full, limit)
		header = [self.format(key, value) for key, value in data.items()]

		return header + statistics

	def listify(self, data, sets, timespans, full, limit):
		"""
		Formats data with multiple data-points into a pretty list.

		Each category is formatted into a header. For each timespan of a given
		category, a list is created if the category holds multiple data-points.
		Lines containing timespans and data-points are formatted into list-items
		using ecstasy.

		Arguments:
			data (dictionary): The data (statistics) to lineify.
			sets (tuple): The names of the sets to include in the output.
			timespans (tuple): The timespans for which to include data.
			full (bool): Whether to show full country names or short
						 ISO abbreviations (e.g. 'Germany' or 'DE').
			limit (int): A limit on the number of data-points retrieved per
						 timespan.
		Returns:
			A list of lines, ready for output.
		"""
		lines = []
		for display, real in sets.items():
			lines.append('{0}:'.format(display.title()))
			for timespan, categories in data.items():
				# Ignore unwanted timespans
				if timespan not in timespans:
					continue
				lines.append(self.get_header(timespan))
				# The goo.gl API does not include categories with zero
				# clicks thus we first have to determine whether the
				# category is present at all
				if not categories.get(real):
					lines[-1] += ' None'
				elif display == 'clicks':
					lines[-1] += ' {0}'.format(categories[real])
				else:
					lines += self.sub_listify(display,
											  categories[real],
											  limit,
											  full)
		return lines

	def get_header(self, timespan):
		"""
		Formats timespan headers.

		Among other things, this method takes care of the 'forever' timespan,
		whose name to the goo.gl API is 'allTime'. Before returning a header,
		it is formatted using ecstasy into a proper, pretty list-item.
		"""
		if timespan == 'allTime':
			header = 'Since forever:'
		else:
			if timespan == 'twoHours':
				timespan = 'two hours'
			header = 'Last {0}:'.format(timespan)

		return self.list_item.format(header)

	def sub_listify(self, category, points, limit, full):
		"""
		Handles transforming data for a category into a level-2 list.

		While listify handles all data and takes care of formatting timespans,
		this method handles only data for a single category. Because this data
		is on the second level of each list (0th level is the category, 1st
		is the timespan and 2nd are the data-points), it is formatted
		differently than the data on level-1 (the level-1 bullet is a '+',
		the level-2 bullet a '-'). This method also handles special cases
		for key-names and also country-name expansion.

		Arguments:
			category (str): The name of the category of this data.
			points (list): The data points for this category (the list
						   contains dictionaries with the keys 'id' and
						   'count').
			limit (int): A limit on the number of data-points retrieved per
						 timespan.
			full (bool): Whether to show full country names or short
						 ISO abbreviations (e.g. 'Germany' or 'DE').
		"""
		lines = []
		for n, point in enumerate(points):
			if n == limit:
				break
			subject = point['id']
			if subject == 'unknown':
				subject = subject.title()
			if category == 'countries' and full:
				subject = lnk.countries.names[subject]
			clicks = point['count']
			line = ecstasy.beautify('   <-> {0}: {1}', ecstasy.Color.Yellow)
			lines.append(line.format(subject, clicks))

		return lines

	def get_timespans(self, times, forever):
		"""
		Parses timespans.

		The timespans passed to the command-line interface and ultimately
		to the fetch() method are of the schema '(<span>, <unit>)'. These
		are parsed such that special cases are handled, e.g. if the 'forever'
		flag is set, the timespan 'allTime' is added for the goo.gl API.
		If no timespans were passed to the method, the default timespan is
		retrieved from the command's configuration settings.

		Arguments:
			times (tuple): The timespans of the schema '(<span>, <unit>)'.
			forever (bool): Whether to include the 'since forever' timespan.

		Returns:
			A set of timespans (string-representations thereof).
		"""
		timespans = set(times)
		if not timespans and not forever:
			default = self.settings['timespan']
			if default == 'forever':
				timespans.add('allTime')
			elif default == 'two-hours':
				timespans.add('twoHours')
			else:
				timespans.add(default)
		if forever:
			timespans.add('allTime')
		if 'two-hours' in timespans:
			timespans.remove('two-hours')
			timespans.add('twoHours')

		return timespans

	@staticmethod
	def format(key, value):
		"""
		Formats a key/value pair for output.

		Handles special cases for key-names and formats the key-value pair.

		Arguments:
			key (str): The key of the data-point.
			value (str): The value of the data-point.

		Returns:
			A pretty key-value string-representation.
		"""
		if key == 'shortUrlClicks':
			key = 'clicks'
		elif key == 'longUrl':
			key = 'expanded'

		return '{0}: {1}'.format(key.title(), value)
