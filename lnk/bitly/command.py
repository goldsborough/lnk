#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Contains the base-class for all bit.ly commands."""

import lnk.config
import lnk.errors

from lnk.abstract import AbstractCommand

class Command(AbstractCommand):
	"""
	Base-class for all bit.ly commands.

	Configures the AbstractCommand base class for all commands in the
	entire application, which needs information about the service being
	used. Moreover sets up the necessary parameters needed for any request
	to the bit.ly API (the OAuth2 access token). 

	Attributes:
		parameters (dict): The necessary parameters for any request to the
						   bit.ly API.
	"""
	def __init__(self, which):
		"""
		Raises:
			errors.AuthorizationError: If the OAuth2 access token cannot be
									   retrieved from the configuration file.
		"""
		super(Command, self).__init__('bitly', which)
		with lnk.config.Manager('bitly') as manager:
			if not manager['key'] and which != 'key':
				raise lnk.errors.AuthorizationError('bitly')
			self.parameters = {'access_token': manager['key']}

	@staticmethod
	def verify(response, what, inner=None):
		"""
		Verifies an HTTP-response from the bit.ly API.

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
			inner (str): If it is expected that data has an inner layer, the
						 key of that inner layer to retrieve the data directly.

		Returns:
			The actual data of the response, if no fault was found.

		Raises:
			errors.HTTPError: If it was found that there was an HTTP-related
							  exception, such as a faulty URL or other badness.
			errors.APIError: If it was found that there was an exception
							 related to the API itself.
		"""
		if not str(response.status_code).startswith('2'):
			raise lnk.errors.HTTPError('Could not {0}.'.format(what),
								   response.status_code,
								   response.reason)
		response = response.json()
		if not str(response['status_code']).startswith('2'):
			raise lnk.errors.HTTPError('Could not {0}.'.format(what),
								   response['status_code'],
								   response['status_txt'])
		data = response['data']
		if inner:
			data = data[inner][0]
		if 'error' in data:
			what = 'Could not {0}!'.format(what)
			raise lnk.errors.APIError(what, data['error'])

		return data
