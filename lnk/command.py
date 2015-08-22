#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import requests

import config
import errors

class Command(object):

	def __init__(self, service, command):
		with config.Manager(service) as manager:
			self.url = manager['url'] + 'v{}'.format(manager['version'])
			self.config = manager['commands'][command]
			self.parameters = {'access_token': manager['key']}
			self.endpoints = self.config.get('endpoints')
			self.http = re.compile(r'https?://')

	def parse(self, *args):
		raise NotImplementedError

	def get(self, endpoint):
		url = '{}/{}'.format(self.url, endpoint)
		response = requests.get(url, params=self.parameters)
		return response.json()

	@staticmethod
	def verify(response, what, sub=None):
		if not str(response['status_code']).startswith('2'):
			raise errors.HTTPError('Could not {}.'.format(what),
								   response['status_code'],
						           response['status_txt'])

		data = response['data'][sub][0] if sub else response['data']

		if 'error' in data:
			what = 'Could not {}.'.format(what)
			raise errors.APIError(what, data['error'])
