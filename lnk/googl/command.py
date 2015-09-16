#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import apiclient.discovery
import googleapiclient.errors
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

	def get_api(self):
		http = self.authorize()
		api = apiclient.discovery.build('urlshortener', 'v1', http=http)

		return api.url()

	def get(self, url, projection=None, what=None):
		api = self.get_api()
		request = api.get(shortUrl=url, projection=projection)
		response = self.execute(request, what)

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

	@staticmethod
	def execute(request, what=None):
		try:
			response = request.execute()
		except googleapiclient.errors.HttpError:
			raise errors.HTTPError('Could not {0}.'.format(what))

		return response

