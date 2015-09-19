#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json

import lnk.errors

def get(which, key):
	"""
	Convenience method to retrieve only one
	key without having to instantiate a Manager object.
	"""
	return Manager(which)[key]

class Manager(object):

	def __init__(self, which=None, write=False):

		path = os.path.abspath(__file__)

		parent = os.path.dirname(os.path.dirname(os.path.dirname(path)))

		self.path = os.path.join(parent, 'config')

		self.write_upon_exit = write
		self.which = which
		self.file = None
		self.config = self.open(which) if which else None

	def open(self, which):
		self.file = os.path.join(self.path, '{0}.json'.format(which))
		with open(self.file) as source:
			self.config = json.load(source)
		return self.config

	def close(self):
		self.assert_open()
		self.file = self.config = None

	def write(self):
		self.assert_open()
		with open(self.file, 'wt') as destination:
			json.dump(self.config, destination, indent=4)

	def assert_open(self):
		if not self.file:
			what = 'No configuration file was ever opened!'
			raise lnk.errors.InternalError(what)

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
		if key not in self.config:
			raise lnk.errors.InvalidKeyError("Key '{0}' not found.".format(key))
		return self.config[key]

	def __setitem__(self, key, value):
		if key not in self.config:
			raise lnk.errors.InvalidKeyError("Key '{0}' not found.".format(key))
		self.config[key] = value

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		if self.write_upon_exit:
			self.write()
		self.close()
