#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""User-information from the bit.ly API."""

from __future__ import unicode_literals

import click
import time

try:
	from collections import OrderedDict
except ImportError:
	from ordereddict import OrderedDict

import lnk.abstract
import lnk.beauty
import lnk.bitly.history

from lnk.bitly.command import Command

def echo(*args):
	"""
	Executes a user command and echoes its output.

	Arguments:
		args (variadic): The arguments to pass to a
						 User instance's fetch() method.
	"""
	click.echo(User().fetch(*args))

class User(Command):
	"""
	Class to user-related information from the bit.ly API.

	User-related information includes data about since when the user
	is a member of bit.ly, the user's full name, the user's privacy
	settings, what share-accounts the user has associated his or her
	account with (e.g. Twitter or Facebook) and other things. Data
	may be put into a pretty string-box, or returned as a raw list
	for internal use.

	Attributes:
		raw (bool): Whether to prettify the output or
					return it raw, for internal use.
		history (bitly.history.History): An instance of bitly.history.History
										 to additionaly fetch link-history data
										 if so requested by the user.
		keys (dict): An additional mapping between the sets (data categories)
					 that the user can include from the command-line and proper
					 string-representations for output.
	"""
	def __init__(self, raw=False):
		super(User, self).__init__('user')
		self.raw = raw
		self.history = lnk.bitly.history.History(raw=True)
		# The point of this is that usually, the keys that the user can
		# supply from the command-line to address a certain data category
		# are fine for output, so there is just one mapping between those
		# categories and the actual names in the data returned by bitly.
		# This mapping is self.sets. Here, now, however, this additional
		# mapping between those category names and the outside-world
		# representation is needed.
		self.keys = {}
		for key, value in self.sets.items():
			if key == 'privacy':
				self.keys[value] = 'Link privacy'
			elif key == 'key':
				self.keys[value] = 'Api key'
			else:
				self.keys[value] = value.replace('_', ' ').title()

	def fetch(self, only, hide, _, add_history, hide_empty):
		"""
		Fetches user information.

		Arguments:
			only (tuple): A tuple of strings representing the sets to include
						  in the response ('only' these will be included).
			hide (tuple): A tuple of strings representing the sets to hide
						  from the response (either from all possible sets
						  if only is empty, or else from those selected).
			_ (bool): A dummy value that is actually the --all/--everything
					  flag for the command-line interface. It is needed from
					  the CLI if no specific data-sets should be included or
					  excluded (=> only/hide), but is of no use here because
					  if only and hide are empty no data-sets will be filtered
					  out anyway.
			add_history (bool): Whether to also show the user's link-history.
			hide_empty (bool): Whether or not to show things that are empty,
							   such as an empty list of share-accounts.

		Returns:
			A plain list of the raw lines if the 'raw' attribute is True,
			else a boxified, pretty string.
		"""
		sets = lnk.abstract.filter_sets(self.sets, only, hide)
		data = self.request(sets.values())
		result = [self.lineify(data, hide_empty)]

		if add_history:
			result.append(self.get_history())
		elif self.raw:
			return result[0]

		return result if self.raw else lnk.beauty.boxify(result)

	def lineify(self, data, hide_empty):
		"""
		Formats the user-data retrieved into a list for output.

		Handles cases where the value for a certain key is a list, such as
		for the share-accounts, as well as if it is just a plain string. Also
		discards empty key/value pairs if hide_empty is true and the value
		is empty (empty iterable or string).

		Arguments:
			data (dict): The user-data retrieved.
			hide_empty (bool): Whether or not to show things that are empty,
							   such as an empty list of share-accounts.

		Returns:
			A list of pretty lines, ready for output.
		"""
		lines = []
		for key, value in data.items():
			if hide_empty and (not value and value != 0):
				continue
			if key == 'share_accounts':
				lines += self.format_accounts(value)
			elif isinstance(value, list):
				lines.append(self.format(key))
				lines += [self.list_item.format(i) for i in value]
			else:
				lines.append(self.format(key, value))

		return lines

	def format_accounts(self, value):
		"""
		Handles formatting of share-accounts.

		Share-accounts have a specific data-format that must be handled
		separately. For each share-account, a string-representation of the
		account-service is given (e.g. Twitter) and also the username for
		that service is displayed (@<username> for Twitter and the user's
		name for Facebook). Each share-account is finally shown as a string
		of the schema '<service>: <username>' and additionaly formatted
		into a pretty list-item.
		"""
		lines = ['Share Accounts:']
		if not value:
			lines[-1] += ' None'
		for account in value:
			if account['account_type'] == 'twitter':
				user = account['account_name']
				line = 'Twitter: @{0}'.format(user)
			elif account['account_type'] == 'facebook':
				user = account['account_name']
				line = 'Facebook: {0}'.format(user)
			else:
				line = account['account_type'].title()
			lines.append(self.list_item.format(line))

		return lines

	def format(self, key, value=''):
		"""
		Formats key/value pairs of user-data information.

		Handles special values and cases where the value is empty. Also
		parses and formats timestamps into proper (ctime) string-
		representations.

		Arguments:
			key (str): The key of the data-point.
			key (?): The value of the data-point.

		Returns:
			A string following the schema '<key>: <value>'.

		"""
		if not value and value != '':
			value = 'None'
		if key == 'member_since':
			value = time.ctime(value)

		return '{0}: {1}'.format(self.keys[key], value)

	def request(self, sets):
		"""
		Requests user-information from the bit.ly API.

		Arguments:
			sets (tuple): The data-categories to include.

		Returns:
			The data retrieved, ordered by the order() method.
		"""
		response = self.get(self.endpoints['user'])
		data = self.verify(response, 'retrieve user info')

		return self.order(data, sets)

	def order(self, data, sets):
		"""
		Partially-sorts user-data according to their priority.

		This method ensures that more important information such as the
		user's full name, his login or his membership-date is displayed
		at the very top of the data returned. This is necessary because
		all data is stored in a dictionary, which is unsorted by default.
		Key/value pairs other than the ones mentioned above are left in
		their original (unsorted) order.

		Arguments:
			data (dict): The raw, retrieved user-data.
			sets (tuple): The allowed categories of user-data.

		Returns:
			A partially-sorted collections.OrderedDict instance with the
			user's full-name in first position, then his or her username,
			then the date of his or her membership and then all other data
			in random order.
		"""
		ordered = OrderedDict()
		# Insert the ones we want on top first
		priority = ['full_name', 'login', 'member_since']
		for key in priority:
			if key in sets:
				ordered[key] = data.pop(key)

		for key, value in data.items():
			if key in sets:
				ordered[key] = value

		return ordered

	def get_history(self):
		"""
		Fetches a user's link-history.

		Uses a bitly.history.History instance.

		Returns:
			A list of links.
		"""
		links = self.history.fetch(None, None, True, None, False, False, False)

		return [self.list_item.format(link) for link in links]
