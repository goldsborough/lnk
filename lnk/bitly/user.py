#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import time

from collections import OrderedDict

import bitly.history

from bitly.command import Command

def echo(*args):
	click.echo(User().fetch(*args))

class User(Command):
	def __init__(self, raw=False):
		super(User, self).__init__('user')
		self.history = bitly.history.History(raw=True)
		self.raw = raw
		self.keys = {}
		for key,value in self.sets.items():
			if key == 'privacy':
				self.keys[value] = 'Link privacy'
			elif key == 'key':
				self.keys[value] = 'Api key'
			else:
				self.keys[value] = value.replace('_', ' ').title()

	def fetch(self, only, hide, _, history, hide_empty):
		sets = self.filter(only, hide)
		data = self.request(sets.values())
		result = self.lineify(data, hide_empty)

		if history:
			result += self.history.fetch()

		return result if self.raw else self.boxify([result])

	def filter(self, only, hide):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for key in hide:
			del sets[key]

		return sets

	def lineify(self, data, hide_empty):
		lines = []
		for key, value in data.items():
			if hide_empty and not value:
				continue
			if isinstance(value, list):
				lines.append(self.format(key))
				lines += [' - {0}'.format(i) for i in value]
			else:
				lines.append(self.format(key, value))

		return lines

	def format(self, key, value=''):
		if not value:
			value = 'None'
		if key == 'member_since':
			value = time.ctime(value)
		return '{0}: {1}'.format(self.keys[key], value)

	def request(self, sets):
		response = self.get(self.endpoints['info'])
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
