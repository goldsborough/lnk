#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import json
import requests

from overrides import overrides

import config
import errors

from abstract import AbstractCommand

class Command(AbstractCommand):
	def __init__(self, which):
		super(Command, self).__init__('googl', which)
		with config.Manager('googl') as manager:
			self.parameters = {'key': manager['key']}

	@staticmethod
	@overrides
	def verify(response, what):
		response = response.json()
		if 'error' in response:
			raise errors.HTTPError('Could not {0}.'.format(what),
								   response['error']['code'],
						           response['error']['message'])

		return response

	@overrides
	def post(self, endpoint, data=None):
		url = '{0}/{1}'.format(self.api, endpoint)
		print(url)
		headers = {'content-type': 'application/json'}
		return requests.post(url,
							 params=self.parameters,
							 data=json.dumps(data),
							 headers=headers)
