#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import ecstasy
import sys

class Error(Exception):

	def __init__(self, what, **additional):
		#\a is the bell character (makes a 'beep' sound)
		additional['Error'] = ('\a{0}'.format(what), 0)
		additional['Type'] = (type(self).__name__, 2)

		self.levels = self.get_levels(additional)

		super(Error, self).__init__(self.what)

	@property
	def what(self):
		return self.levels[0][0]

	@staticmethod
	def get_levels(additional):
		# Each nested list corresponds to one further level of verbosity
		levels = [[], [], [], []]
		for key, value in additional.items():
			if key and value:
				level = 1 # default
				if isinstance(value, tuple):
					level = value[1]
					value = value[0]
				line = '<{0}>: {1}'.format(key, value)
				line = ecstasy.beautify(line, ecstasy.Color.Red)
				levels[level].append(line)

		return ['\n'.join(level) for level in levels if level]

class HTTPError(Error):
	def __init__(self, what, code=None, status=None):
		super(HTTPError, self).__init__(what, Code=code, Status=status)

class APIError(Error):
	def __init__(self, what, message=None):
		super(APIError, self).__init__(what, Message=message)

class UsageError(Error):
	def __init__(self, what):
		super(UsageError, self).__init__(what)

class InvalidKeyError(Error):
	def __init__(self, what):
		super(InvalidKeyError, self).__init__(what)

class InternalError(Error):
	"""
	Raised when something went wrong internally, i.e.
	within methods that are non-accessible via the
	API but are used for internal features or processing.
	Basically get mad at the project creator.
	"""

	def __init__(self, what):
		"""
		Initializes the Error super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""
		super(InternalError, self).__init__(what)

class Catch(object):

	def __init__(self, verbosity=0, usage=None):
		self.verbosity = verbosity
		self.usage = usage

	def catch(self, function, *args, **kwargs):
		try:
			try:
				function(*args, **kwargs)
			except click.ClickException:
				_, e, _ = sys.exc_info()
				# Re-raise as an error we can handle (and format)
				raise UsageError(e.message)
		except Error:
			_, e, _ = sys.exc_info()
			click.echo('\n'.join(e.levels[:self.verbosity + 1]))
			if self.usage:
				click.echo(self.usage)

def catch(function, *args, **kwargs):
	"""Convenience function for a Catch object with default verbosity (0)."""
	Catch().catch(function, *args, **kwargs)

def warn(what):
	what = "\a<Warning>: {}".format(what)
	click.echo(ecstasy.beautify(what, ecstasy.Color.Yellow))
