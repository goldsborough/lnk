#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import time

from collections import OrderedDict

import beauty
import bitly.history

from bitly.command import Command, filter_sets

def echo(*args):
	click.echo(User().fetch(*args))

class User(Command):
	def __init__(self, raw=False):
		super(User, self).__init__('user')
		self.history = bitly.history.History(raw=True)
		self.raw = raw
		self.keys = {}
		for key, value in self.sets.items():
			if key == 'privacy':
				self.keys[value] = 'Link privacy'
			elif key == 'key':
				self.keys[value] = 'Api key'
			else:
				self.keys[value] = value.replace('_', ' ').title()

	def fetch(self, only, hide, _, add_history, hide_empty):
		sets = filter_sets(self.sets, only, hide)
		data = self.request(sets.values())
		result = [self.lineify(data, hide_empty)]

		if add_history:
			result.append(self.get_history())
		elif self.raw:
			return result[0]

		return result if self.raw else beauty.boxify(result)

	def lineify(self, data, hide_empty):
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
		lines = ['Share Accounts:']
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
		if not value and value != '':
			value = 'None'
		if key == 'member_since':
			value = time.ctime(value)

		return '{0}: {1}'.format(self.keys[key], value)

	def request(self, sets):
		response = self.get(self.endpoints['user'])
		data = self.verify(response, 'retrieve user info')

		return self.order(data, sets)

	def order(self, data, sets):
		ordered = OrderedDict()

		# Insert the ones we want on top first
		priority = ['full_name', 'login', 'member_since']
		for key in priority:
			if key in sets:
				ordered[key] = data.pop(key)

		for key,value in data.items():
			if key in sets:
				ordered[key] = value

		return ordered

	def get_history(self):
		links = self.history.fetch(None, None, True, None, False, False, False)

		return [self.list_item.format(link) for link in links]
