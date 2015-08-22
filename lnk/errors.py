#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import ecstasy
import sys

class Error(Exception):

	def __init__(self, what, **additional):
		additional['Type'] = (type(self).__name__, 2)
		additional['Error'] = (what, 0)

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

		#\a is the bell character (makes a 'beep' sound)
		self.what = '\a{0}'.format(levels[0][0])
		self.verbose = ['\n'.join(level) for level in levels if level]

		super(Error, self).__init__(self.what)

class HTTPError(Error):
	def __init__(self, what, code=None, status=None):
		super(HTTPError, self).__init__(what, Code=code, Status=status)

class APIError(Error):
	def __init__(self, what, message=None):
		super(APIError, self).__init__(what, Message=message)

class ParseError(Error):
	def __init__(self, what):
		super(ParseError, self).__init__(what)

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

def warn(what):
	what = "\a<Warning>: {}".format(what)
	click.echo(ecstasy.beautify(what, ecstasy.Color.Yellow))

def catch(verbose, action, *args, **kwargs):
	if sys.version_info[0] < 3:
		try:
			action(*args, **kwargs)
		except Error, e:
			click.echo('\n'.join(e.verbose[:verbose + 1]))
	else:
		try:
			action(*args, **kwargs)
		except Error as e:
			click.echo('\n'.join(e.verbose[:verbose + 1]))
