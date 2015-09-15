#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import apiclient.discovery
import httplib2
import oauth2client.file
import os

from overrides import overrides

import config
import errors

from abstract import AbstractCommand

class Command(AbstractCommand):
	def __init__(self, which):
		super(Command, self).__init__('googl', which) 
		credentials_path = os.path.join(config.CONFIG_PATH, 'credentials')
		self.credentials = oauth2client.file.Storage(credentials_path)

	@staticmethod
	@overrides
	def verify(response, what):
		if 'error' in response:
			raise errors.HTTPError('Could not {0}.'.format(what),
								   response['error']['code'],
						           response['error']['message'])

	def get_api(self):
		http = self.authorize()
		api = apiclient.discovery.build('urlshortener', 'v1', http=http)

		return api.url()

	def get(self, url, projection=None):
		api = self.get_api()
		request = api.get(shortUrl=url, projection=projection)
		response = request.execute()

		return response

	def authorize(self):
		credentials = self.credentials.get()
		if not credentials:
			raise errors.AuthorizationError('goo.gl')
		http = httplib2.Http()
		if credentials.access_token_expired:
			credentials.refresh(http)
			self.credentials.put(credentials)
		credentials.authorize(http)

		return http
