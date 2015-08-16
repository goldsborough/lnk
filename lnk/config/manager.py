#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json

import errors

class Manager(object):

	def __init__(self, name):

		path = os.path.abspath(__file__)

		parent = os.path.dirname(os.path.dirname(os.path.dirname(path)))

		self.path = os.path.join(parent, 'config')

		self.file = None
		self.config = None

		self.open(name)

	def open(self, name):
		self.file = os.path.join(self.path, '{}.json'.format(name))
		with open(self.file) as config:
			self.config = json.load(config)

	def close(self):
		if not self.file:
			raise errors.InternalError("No configuration file was ever opened!")
		self.file = self.config = None

	def write(self):
		with open(self.file, 'wt') as config:
			json.dump(self.config, config, indent=4)

	@property
	def keys(self):
		return self.config.keys()

	@property
	def values(self):
		return self.config.values()

	@property
	def items(self):
		return self.config.items()

	def __getitem__(self, key):
		return self.config[key]

	def __setitem__(self, key, value):
		self.config[key] = value

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.write()