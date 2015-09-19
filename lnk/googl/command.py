#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Contains the base-class for all goo.gl commands."""

import apiclient.discovery
import googleapiclient.errors
import httplib2
import oauth2client.file
import os

import lnk.config
import lnk.errors

from lnk.abstract import AbstractCommand

class Command(AbstractCommand):
	"""
	Base-class for all goo.gl commands.

	Configures the AbstractCommand base class for all commands in the
	entire application, which needs information about the service being
	used. Moreover fetches the oauth2 credentials for any HTTP request.

	Attributes:
		credentials (oauth2client.file.Storage): An object from Google's
												 API-library used to interact
												 with the oauth2 credentials
												 file.
	"""
	def __init__(self, which, credentials_path=None):
		"""
		Constructs a new Command.

		Arguments:
			which (str): The name of the command (e.g. link).
			credentials_path (str): Optionally, the full path to a credentials
									file. The one at lnk/config/credentials
									will be chosen by default.
		"""
		super(Command, self).__init__('googl', which) 
		if not credentials_path:
			credentials_path = os.path.join(lnk.config.CONFIG_PATH,
											'credentials')
		self.credentials = oauth2client.file.Storage(credentials_path)

	def get_api(self):
		"""
		Returns an API-object used to perform any request.

		Returns:
			An API object from Google API-library, used to perform any
			HTTP request for the url-shortening API.
		"""
		http = self.authorize()
		api = apiclient.discovery.build('urlshortener', 'v1', http=http)

		return api.url()

	def get(self, url, projection=None, what=None):
		"""
		Base method to perform an HTTP request with the GET method.

		Arguments:
			url (str): The short goo.gl URL for which to perform a data-request.
			projection (str|None): Controls the amount of data returned for
								   the url (values should be either None,
								   such as for url-expansion, or 'FULL' to get
								   statistics or information about a link).
			what (str): A human-readable string representing what the request
						was for, such that if there is an error in the response,
						an errors.HTTPError is raised with the message 
						'Could not <what>.' (NOT: 'even').

		Return:
			The requested data.
		"""
		api = self.get_api()
		request = api.get(shortUrl=url, projection=projection)
		response = self.execute(request, what)

		return response

	def authorize(self):
		"""
		Handles the authorization and re-authorization procedure.

		Normally, this method will return an HTTP object from Google's httplib2
		library, authorized to fetch user-specifc data by using the credentials
		that were configured for the user. There are two other cases: The oauth2
		access-token used to make oauth2 requests expires around-about every
		hour, so if that is the case this method will first refresh the token;
		if there are no credentials at all (i.e. the user did not run the 'key'
		command yet), this method throws an exception.

		Returns:
			If all goes well, an oauth2-authorized httplib2.HTTP object.

		Raises:
			errors.AuthorizationError: If there are no credentials for this user
									   yet (the initial authorization-procedure
									   was not yet performed).
		"""
		credentials = self.credentials.get()
		if not credentials:
			raise lnk.errors.AuthorizationError('goo.gl')
		http = httplib2.Http()
		if credentials.access_token_expired:
			credentials.refresh(http)
			self.credentials.put(credentials)
		credentials.authorize(http)

		return http

	@staticmethod
	def execute(request, what=None):
		"""
		Execute an HTTP request.

		The main point of this method is to catch HTTP errors raised by Google's
		API-library and re-raise them as lnk.errorrs.HTTPErrors.
		"""
		try:
			response = request.execute()
		except googleapiclient.errors.HttpError:
			raise lnk.errors.HTTPError('Could not {0}.'.format(what))

		return response
