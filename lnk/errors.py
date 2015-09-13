#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import ecstasy
import requests
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
	def __init__(self, what, code=None, status=None, **additional):
		super(HTTPError, self).__init__(what,
										Code=code,
										Status=status,
										**additional)

class APIError(Error):
	def __init__(self, what, message=None, **additional):
		super(APIError, self).__init__(what, Message=message, **additional)

class UsageError(Error):
	def __init__(self, what, **additional):
		super(UsageError, self).__init__(what, **additional)

class InvalidKeyError(Error):
	def __init__(self, what, **additional):
		super(InvalidKeyError, self).__init__(what, **additional)

class ConnectionError(Error):
	def __init__(self, what, **additional):
		super(ConnectionError, self).__init__(what, **additional)

class AuthorizationError(Error):
	def __init__(self,
				service,
				what='Missing authorization code!',
				**additional):
		logo = ecstasy.beautify('<lnk>', ecstasy.Style.Bold)
		details = 'You have not yet authorized {0} to '.format(logo)
		details += 'access your private {0} information. '.format(service)
		details += "Please run 'lnk {0} key --generate'.".format(service)
		super(AuthorizationError, self).__init__(what,
												 Details=details,
												 **additional)

class InternalError(Error):
	"""
	Raised when something went wrong internally, i.e.
	within methods that are non-accessible via the
	API but are used for internal features or processing.
	Basically get mad at the project creator.
	"""

	def __init__(self, what, **additional):
		"""
		Initializes the Error super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""
		super(InternalError, self).__init__(what, **additional)

class Catch(object):

	def __init__(self, verbosity=0, usage=None, service=None):
		self.verbosity = verbosity
		self.usage = usage
		self.service = '{0} '.format(service) if service else ''

	def catch(self, function, *args, **kwargs):
		"""Executes a function and handles any potential exceptions."""
		try:
			try:
				function(*args, **kwargs)
			except click.ClickException:
				_, error, _ = sys.exc_info()
				# Re-raise as an error we can handle (and format)
				raise UsageError(error.message)
			except requests.exceptions.ConnectionError:
				_, error, _ = sys.exc_info()
				raise ConnectionError('Could not establish connection '
									  'to {0}server!'.format(self.service))
		except Error:
			_, error, _ = sys.exc_info()
			click.echo('\n'.join(error.levels[:self.verbosity + 1]))
			if isinstance(error, UsageError) and self.usage:
				click.echo(self.usage)

def catch(function, *args, **kwargs):
	"""Convenience function for a Catch object with default verbosity (0)."""
	Catch().catch(function, *args, **kwargs)

def warn(what):
	what = "\a<Warning>: {}".format(what)
	formatted = ecstasy.beautify(what, ecstasy.Color.Yellow)
	click.echo(formatted)
