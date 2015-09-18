#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Information-retrieval for goo.gl link."""

from __future__ import unicode_literals

import click

from datetime import datetime

import lnk.abstract
import lnk.beauty

from lnk.googl.command import Command

def echo(*args):
	"""
	Executes an info command and echoes its output.

	Arguments:
		args (variadic): The arguments to pass to an
						 Info instance's fetch() method.
	"""
	click.echo(Info().fetch(*args))

class Info(Command):
	"""
	Class to retrieve information about a goo.gl link.

	Information about a link may include when it was created, its expanded
	url and its status. This information is returned in a pretty list. The
	list can be put into a box for terminal output, or can be returned raw
	for internal use (such as by the stats command).

	Note:
		A 'goo.gl link' is a link shortened with bit.ly.

	Attributes:
		raw (bool): Whether or not to return the output as a raw list,
					or as a string, in a box.
		sets (dict): A complete dictionary of the available sets of information.
		reverse (dict): A reverse mapping of the above-mentioned sets.
	"""
	def __init__(self, raw=False):
		super(Info, self).__init__('info')

		self.raw = raw
		self.sets = self.config['sets']
		# Dictionary comprehensions not available for Python < 2.7
		self.reverse = dict((value, key) for key, value in self.sets.items())

	def fetch(self, only, hide, urls):
		"""
		Fetches the link information.

		Arguments:
			only (tuple): A tuple of strings representing the sets to include
						  in the response ('only' these will be included).
			hide (tuple): A tuple of strings representing the sets to hide
						  from the response (either from all possible sets
						  if only is empty, or else from those selected).
			urls (tuple): A tuple of urls to fetch information for.

		Returns:
			A plain list of the raw lines if the 'raw' attribute is True,
			else a boxified, pretty string.
		"""
		sets = lnk.abstract.filter_sets(self.sets, only, hide)
		result = []
		threads = []
		for url in urls:
			self.queue.put(url.strip())
			t = self.new_thread(self.get_info, sets.values(), result)
			threads.append(t)
		self.join(threads)

		return result if self.raw else lnk.beauty.boxify(result)

	def get_info(self, sets, result):
		"""
		Requests all information about a url.

		This method is run in a separate thread for each URL, and as such
		uses a queue to get a URL and then appends the information to the
		list supplied in the argument. This is done in a thread-safe, locked
		way.

		Arguments:
			sets (dict): The sets of information to include in the data.
			result (list): The list of results for each URL, to which to
						   append the data requested.
		"""
		url = self.queue.get()
		data = self.request(url)
		selection = dict((key, data[key]) for key in data if key in sets)
		lines = self.lineify(url, selection)
		with self.lock:
			result.append(lines)

	def request(self, url):
		"""
		Requests information for a url.

		Arguments:
			url (str): The goo.gl link to request information for.

		Returns:
			The information for the link supplied.
		"""
		what = "get information for '{0}'".format(url)
		response = self.get(url, 'FULL', what)

		return response

	def lineify(self, url, data):
		"""
		Returns a list of lines for given (information) data.

		The lines returned include a header with the relevant URL,
		followed by string-formatted key/value pairs.

		Arguments:
			url (str): The URL of which the data should be formatted.
			data (dict): The data (information) for the url.
		Returns:
			A list of lines, ready for output.
		"""
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			lines.append(self.format(key, value))

		return lines

	def format(self, key, value):
		"""
		Handles formatting of a data-point.

		Handles parsing of the ISO-8601-formatted timestamp from Google's API
		into a proper string-representation (ctime). Also formats the key-value
		pair.

		Arguments:
			key (str): The key of the data-point.
			value (str): The value of the data-point.

		Returns:
			A formatted string of the schema '<key>: <value>'.
		"""
		key = self.reverse[key]
		if key == 'created':
			# Ignore the irrelevant part of the ISO format
			relevant = value[:value.find('.')]
			parsed = datetime.strptime(relevant, '%Y-%m-%dT%H:%M:%S')
			value = parsed.ctime()

		return '{0}: {1}'.format(key.title(), value)
