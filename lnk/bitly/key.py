#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Handles the oauth2 authorization procedure for the bit.ly API."""

import click
import simplejson

import beauty
import config
import errors

from bitly.command import Command

CLIENT_ID = '049118cdcf01c6b267f77582990d48da9127259a'
CLIENT_SECRET = 'b5257382fd1c7118688cae7942d5128b4d995c9e'

def echo(*args):
	"""
	Executes a history command and echoes its output.

	Arguments:
		args (variadic): The arguments to pass to a
						 History instance's fetch() method.
	"""
	click.echo(Key().fetch(*args), nl=False)

class Key(Command):
	"""
	Handles oauth2 authorization for the bit.ly API.

	The bulk of the work is done by the user in the command-line interface.
	When 'lnk bitly --key' is run (or 'lnk --key' if bitly is the default),
	the user is prompted for his or her login and password. This information
	is passed to this class, which then fetches an oauth2 access-token using
	the appropriate exchange procedure.

	Attributes:
		raw (bool): Whether or not to return the raw output for internal use
					or the prettified output for outside representation.
	"""
	def __init__(self, raw=False):
		super(Key, self).__init__('key')
		self.raw = raw
		self.parameters['client_id'] = CLIENT_ID
		self.parameters['client_service'] = CLIENT_SECRET

	def fetch(self, _, login, password, show):
		"""
		Fetches an oauth2 access-token for a given login and password.

		Arguments:
			_: This is the --generate flag, just a dummy parameter because it
			   must be passed from the command-line to initiate the procedure
			   but has no actual use here.
			login (str): The user's login (username).
			password (str): The user's password.
			show (bool): Whether or not to return the access-token for output
						 once retrieved.

		Returns:
			If the show flag is set, the raw key as a string if self.raw
			is True, else the key in a pretty box. If the show flag is unset,
			an empty string is returned (such that nothing appears in the
			command-line output).
		"""
		key = self.request(login, password)
		with config.Manager('bitly', write=True) as manager:
			manager['key'] = key

		if show:
			if self.raw:
				return key
			return beauty.boxify([[key]]) + '\n'
		return ''

	def request(self, login, password):
		"""
		Requests an oauth2 token from the bit.ly API.

		Arguments:
			login (str): The user's login (username).
			password (str): The user's password.

		Returns:
			The oauth2 token/key, if the request was successful.

		Raises:
			Any errors thrown by the verify() method.
		"""
		response = self.post(self.endpoints['oauth'],
							 authorization=(login, password))

		key = self.verify(response, 'generate an API key')

		return key

	@staticmethod
	def verify(response, what):
		"""
		Verifies the HTTP response following the request for an oauth2 token.

		Arguments:
			response (requests.Response): The HTTP-response from the request
										  for an oauth2 token.
			what (str): A string-representation of what the request was for,
						such that if an error is found and raised, its message
						is 'Could not <what>' (e.g. 'generate an API key').

		Returns:
			The plain, string oauth2 access-token.

		Raises:
			errors.HTTPError: If an HTTP-related fault was found in the response.
		"""
		# If the request succeeded, the response is in
		# text format, so the json decoding would fail,
		# if there was an error we have to retrieve it in json
		try:
			response = response.json()
			if not str(response['status_code']).startswith('2'):
				raise errors.HTTPError('Could not {}.'.format(what),
									   response['status_code'],
							           response['status_txt'])
		except simplejson.scanner.JSONDecodeError:
			pass

		return str(response.text)
