#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import ecstasy

class Error(Exception):
	def __init__(self, what, **additional):

		self.what = ecstasy.beautify("\a<Error>: {}".format(what),
									 ecstasy.Color.Red)

		self.verbose = self.what

		for i, j in additional.items():
			# Might be None
			if j: 
				self.verbose += ecstasy.beautify("\n<{}>: {}".format(i, j),
												 ecstasy.Color.Red)

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
	print(ecstasy.beautify("\a<Warning>: {}".format(what), 
						   ecstasy.Color.Yellow))
