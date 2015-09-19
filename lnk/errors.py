#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Custom error classes + error handling and warning mechanisms.

All non-standard errors raised by lnk should be defined here.
"""

import click
import ecstasy
import googleapiclient.errors
import re
import requests
import sys

from collections import namedtuple

Message = namedtuple('Message', ['what', 'level'])

class Error(Exception):
	"""
	Exception base class for all errors.

	Implements a system of multiple verbosity levels
	such that error output can be controlled according
	to the verbosity setting specified by the user
	(how many -v are passed).

	Attributes:
		what (str): A plain string message specifying what happened.
		levels (list): A list of strings for each verbosity level.
	"""

	def __init__(self, what, **additional):
		self.what = what or 'Something bad happened.'

		#\a is the bell character (makes a 'beep' sound)
		additional['Error'] = Message('\a{0}'.format(self.what), 0)
		additional['Type'] = Message(type(self).__name__, 2)

		self.levels = self.get_levels(additional)

		super(Error, self).__init__(self.what)

	def level(self, verbosity):
		"""
		Fetches a list of all non-empty levels for a given verbosity.

		Arguments:
			verbosity (int): The verbosity level (e.g. 0 for 'what').

		Returns:
			All levels for the given verbosity, but filtering out
			empty ones.
		"""
		levels = self.levels[:verbosity + 1]

		return [i for i in levels if i]

	@staticmethod
	def get_levels(additional):
		"""
		Transforms and formats error levels.

		Each additional level passed to the constructor of
		Error is either the error string, in which case its level
		is 1 or a Error.Message tuple consisting of that same
		error string and additionally an integer specifying the
		level. This information is parsed here, such that the
		result is a list of level strings. Moreover, each
		key/value pair of each error message is formatted
		with ecstasy to make it look pretty.

		Arguments:
			additional (dict): The additional error messages.

		Returns:
			A list of strings for each level of verbosity.
		"""
		# Each nested list corresponds to one further level of verbosity
		levels = [[], [], [], []]
		for key, value in additional.items():
			if key and value:
				level = 1 # default
				if isinstance(value, Message):
					level = value.level
					value = value.what
				line = '<{0}>: {1}'.format(key, value)
				line = ecstasy.beautify(line, ecstasy.Color.Red)
				levels[level].append(line)

		return ['\n'.join(level) if level else None for level in levels]

class HTTPError(Error):
	"""
	Raised in case of a faulty HTTP request.

	Usually because the data provided by the user was ill-formed
	(such as an expanded url where a shortened one is expected).
	Additionally may have a code and status information.
	"""
	def __init__(self, what, code=None, status=None, **additional):
		super(HTTPError, self).__init__(what,
										Code=code,
										Status=status,
										**additional)

class APIError(Error):
	"""
	Raised if there was a problem communicating with the API.

	Meaning if the problem was not ill-formed data as is the case
	for an HTTPError, but something specific to the API (possibly
	associated with its key/access-token).
	"""
	def __init__(self, what, message=None, **additional):
		super(APIError, self).__init__(what, Message=message, **additional)

class UsageError(Error):
	"""
	Raised for invalid command-line usage.

	A UsageError is raised by lnk if some cli-related badness is not
	handled by click (such as misisng urls). If invalid command-line
	usage is handled by click, this is detected and click's exception
	is then re-raised as a UsageError (i.e. any faulty cli input is
	always reported as an error of this type).
	"""
	def __init__(self, what, **additional):
		super(UsageError, self).__init__(what, **additional)

class InvalidKeyError(Error):
	"""
	Raised when an invalid key is passed to the config command.
	"""
	def __init__(self, what, **additional):
		super(InvalidKeyError, self).__init__(what, **additional)

class ConnectionError(Error):
	"""
	Raised if there was a problem connecting with the API.

	(Usually if the user is not connected to the interwebs).
	"""
	def __init__(self, what, hint=None, **additional):
		hint = hint or 'Are you connected to the webs?'
		super(ConnectionError, self).__init__(what, Hint=hint, **additional)

class AuthorizationError(Error):
	"""
	Raised in case of an authorization error.

	This is mostly the case initially, when the user first runs
	lnk and has noet yet authenticated himself and authorized
	lnk to access private information (such as user data for bitly).
	"""
	def __init__(self,
				service,
				what='Missing authorization code!',
				**additional):
		logo = ecstasy.beautify('<lnk>', ecstasy.Style.Bold)
		details = 'You have not yet authorized {0} to '.format(logo)
		details += 'access your private {0} information. '.format(service)
		hint = "Run 'lnk {0} key --generate'.".format(service)
		super(AuthorizationError, self).__init__(what,
												 Details=details,
												 Hint=hint,
												 **additional)

class InternalError(Error):
	"""
	Raised when something went wrong internally.

	Will be thrown only within methods that are non-accessible via
	the API but are used forinternal features or processing.
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

	"""
	Exception-handling class.

	Catch is essentially a interface to its main method 'catch',
	but adds the ability to add a usage string that is displayed
	optionally in case of a UsageError, and also the service being
	used while the exception is thrown. The information about the
	url-shortening service is of use for ConnectionErrors.

	Attributes:
		verbosity (int): The verbosity level (defaults to 0).
		usage (str): Optionally, a usage string to display for UsageErrors.
		service (str): The url-shortening service currently in use.
	"""

	def __init__(self, verbosity=0, usage=None, service=None):
		self.verbosity = verbosity
		self.usage = usage
		self.service = '{0} '.format(service) if service else ''

	def catch(self, function, *args, **kwargs):
		"""
		Executes a function and handles any potential exceptions.

		Arguments:
			function (func): The function to execute.
			args (variadic): The positional arguments to pass to the function call.
			kwargs (variadic): The keyword arguments to pass to the function call.
		"""
		try:
			try:
				function(*args, **kwargs)
			# Re-raise as an error we can handle (and format)
			except click.ClickException:
				error = self.get_error()
				raise UsageError(error.message)
			except googleapiclient.errors.HttpError:
				self.handle_google_error()
			except requests.exceptions.ConnectionError:
				error = self.get_error()
				raise ConnectionError('Could not establish connection '
									  'to {0}server!'.format(self.service))
			except click.exceptions.Abort:
				click.echo() # Just the newline 
		except Error:
			self.handle_error()

	def handle_error(self):
		"""
		Handles an Error.

		Takes care of retrieveing the error message string from the
		Error that is appropriate to the verbosity level passed to
		the constructor of Catch. This message string is then printed
		to stdout. If the Error was a UsageError, the usage string
		is printed too.
		"""
		error = self.get_error()
		click.echo('\n'.join(error.level(self.verbosity)))
		if isinstance(error, UsageError) and self.usage:
			click.echo(self.usage)

	@staticmethod
	def handle_google_error():
		"""
		Handles exceptions raised by the goo.gl api client.

		Exceptions raised by the goo.gl api client do not make
		any error clean message available, but only a long, formatted
		string ready for output. This method takes care of retrieving
		the actualy 'reason' for the exception via regular expressions.
		This reason is then re-raised as an HTTPError that can be handled
		by Catch.
		"""
		error = Catch.get_error()
		match = re.search(r'<HttpError.+returned "([\w\s]+)">$',
						  str(error))
		what = '{0}.'.format(match.group(1))
		if what == 'Required.':
			what = 'Invalid link.'

		raise HTTPError(what)

	@staticmethod
	def get_error():
		"""Retrieves the last error raised in the system."""
		# type, value, traceback
		_, error, _ = sys.exc_info()

		return error

def catch(function, *args, **kwargs):
	"""
	Convenience function for a Catch object with default settings.

	Arguments:
		function (func): The function to execute.
		args (variadic): The positional arguments to pass to the function call.
		kwargs (variadic): The keyword arguments to pass to the function call.
	"""
	Catch().catch(function, *args, **kwargs)

def warn(what):
	"""
	Outputs and formats a warning.

	Arguments:
		what (str): The warning string to output.
	"""
	what = '\a<Warning>: {0}'.format(what)
	formatted = ecstasy.beautify(what, ecstasy.Color.Yellow)
	click.echo(formatted)
