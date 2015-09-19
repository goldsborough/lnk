#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Contains the base-class for all bit.ly commands."""

import lnk.config
import lnk.errors

from lnk.abstract import AbstractCommand

class Command(AbstractCommand):
	"""
	Base-class for all tinyurl commands.

	Configures the AbstractCommand base class for all commands in the
	entire application, which needs information about the service being
	used. Moreover sets up the necessary parameters needed for any request
	to the bit.ly API (the api-key, the response-format and the provider).

	Attributes:
		parameters (dict): The necessary parameters for any request to the
						   tinyurl API.
	"""
	def __init__(self, which):
		super(Command, self).__init__('tinyurl', which)
		with lnk.config.Manager('tinyurl') as manager:
			self.parameters = {'apikey': manager['key']}
		self.parameters['format'] = 'json'
		self.parameters['provider'] = 'tinyurl_com'

	@staticmethod
	def verify(response, what):
		"""
		Verifies an HTTP-response from the tinyurl API.

		Overrides the 'pure-virtual' (i.e. not-implemented) base method
		from AbstractCommand. If the verification finds no faults in the
		response, the data is returned.

		Arguments:
			response (requests.Response): The HTTP response to a request
										  to the bit.ly API.
			what (str): A human-readable string representing what the request
						was for, such that if there is an error in the response,
						an errors.HTTPError or errors.APIError is raised with
						the message 'Could not <what>.'

		Returns:
			The actual data of the response, if no fault was found.

		Raises:
			errors.HTTPError: If it was found that there was an HTTP-related
							  exception, such as a faulty URL or other badness.
		"""
		if not str(response.status_code).startswith('2'):
			raise lnk.errors.HTTPError('Could not {0}!'.format(what),
								   response.status_code,
								   response.reason)
		data = response.json()
		if data['state'] == 'error':
			what = 'Could not {0}!'.format(what)
			raise lnk.errors.APIError(what)

		return data
