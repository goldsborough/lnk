#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Information-retrieval for bitlink."""

from __future__ import unicode_literals

import click
import time

import lnk.abstract
import lnk.beauty

from lnk.bitly.command import Command

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
	Class to retrieve information about a bitlink.

	Information about a link may include when it was created, its expanded
	url, its tags, any note associated with it, when it was last modified
	and other things. This information is returned in a pretty list. The
	list can be put into a box for terminal output, or can be returned raw
	for internal use (such as by the stats command). Note that the information
	retrieved combines data from the /info and user/link_history endpoints.

	Note:
		A 'bitlink' is a link shortened with bit.ly.

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
		# Dictionary comprehensions don't work for Python < 2.7
		self.reverse = dict((value, key) for (key, value) in self.sets.items())

	def fetch(self, only, hide, hide_empty, urls):
		"""
		Fetches the link information.

		Arguments:
			only (tuple): A tuple of strings representing the sets to include
						  in the response ('only' these will be included).
			hide (tuple): A tuple of strings representing the sets to hide
						  from the response (either from all possible sets
						  if only is empty, or else from those selected).
			hide_empty (bool): Whether or not to show things that are empty,
							   such as an empty list of tags.
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
			t = self.new_thread(self.request, sets.values(), result, hide_empty)
			threads.append(t)
		self.join(threads)

		return result if self.raw else lnk.beauty.boxify(result)

	def request(self, sets, result, hide_empty):
		"""
		Requests all information about a url.

		The information returned for a URL is a combination of the data
		retrieved from the /info endpoint, and the data retrieved from the
		/user/link_history endpoint. Both these sets of information are
		retrieved here and combined into one set of information for a URL.
		This method is run in a separate thread for each URL, and as such
		uses a queue to get a URL and then appends the information to the
		list supplied in the argument. This is done in a thread-safe, locked
		way.

		Arguments:
			sets (dict): The sets of information to include in the data.
			result (list): The list of results for each URL, to which to
						   append the data requested.
			hide_empty(bool): Whether or not to hide empty things, passed on
							  to lineify.
		"""
		url = self.queue.get()
		data = self.request_info(url)
		data.update(self.request_history(url))

		selection = dict((key, data[key]) for key in data if key in sets)
		lines = self.lineify(url, selection, hide_empty)

		with self.lock:
			result.append(lines)

	def request_info(self, url):
		"""
		Requests information for a url.

		Requests the part of the information that can be fetched from the /info
		endpoint.

		Arguments:
			url (str): The bitlink to request information for.

		Returns:
			The information for the bitlink supplied.
		"""
		response = self.get(self.endpoints['info'], dict(shortUrl=url))
		response = self.verify(response,
							   "retrieve information for '{0}'".format(url),
							   'info')

		return response

	def request_history(self, url):
		"""
		Requests more information for a url.

		Requests the part of the information that can be fetched from the
		/user/link_history endpoint. This request requires oauth2 authorization.

		Arguments:
			url (str): The bitlink to request information for.

		Returns:
			The information for the bitlink supplied.
		"""
		response = self.get(self.endpoints['history'], dict(link=url))
		response = self.verify(response,
				   			   "retrieve additional "
				   			   "information for '{0}'".format(url),
				   			   'link_history')

		return response

	def lineify(self, url, data, hide_empty):
		"""
		Returns a list of lines for given (information) data.

		The lines returned include a header with the relevant URL,
		followed by string-formatted key/value pairs. If the value for
		a given key is a list, this list is further formatted and prettified.

		Arguments:
			url (str): The URL of which the data should be formatted.
			data (dict): The data (information) for the url.
			hide_empty (bool): Whether or not to hide empty things, such
							   as an empty list of tags.
		Returns:
			A list of lines, ready for output.
		"""
		lines = ['URL: {0}'.format(url)]
		for key, value in data.items():
			# 0 does not mean empty, while an empty
			# list/tuple/iterable and also string does
			if hide_empty and (not value and value != 0):
				continue
			if isinstance(value, list):
				lines.append(self.format(key, value))
				# A list item is of the schema ' + <thing>'
				# where the plus is in red color
				lines += [self.list_item.format(i) for i in value]
			else:
				lines.append(self.format(key, value))

		return lines

	def format(self, key, value):
		"""
		Handles formatting of a data-point.

		Handles cases in which the representation of a key or value is not
		directly suitable for output, such as when the value is a UNIX
		timestamp, which should really be formatted into a proper ctime
		representation. Also changes booleans into 'Yes'/'No'.

		Arguments:
			key (str): The key of the data-point.
			value (str): The value of the data-point.

		Returns:
			A formatted string of the schema '<key>: <value>'. What '<key>'
			and '<value>' end up being is highly-dependent on the actual
			values of the arguments.
		"""
		# The key is now what is returned from the bit.ly API, usually
		# something ugly such as 'created_at'. This must be
		# reverse-mapped to the string-representation used by lnk.
		key = self.reverse[key]
		if key == 'created' or key == 'modified':
			value = time.ctime(value)
		elif key == 'user' and value is None:
			value = 'Not public'
		elif key == 'privacy':
			# the set is '--only privacy', but
			# want to display 'Private: ...'
			key = 'private'

		if isinstance(value, bool):
			value = 'Yes' if value else 'No'
		elif not value:
			value = 'None'
		elif isinstance(value, list):
			value = ''

		return '{0}: {1}'.format(key.title(), value)
