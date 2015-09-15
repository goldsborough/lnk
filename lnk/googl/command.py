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
		if not str(response.status_code).startswith('2'):
			raise errors.HTTPError('Could not {0}.'.format(what),
								   response.status_code,
						           response.reason)
		response = response.json()
		if 'error' in response:
			raise errors.HTTPError('Could not {0}.'.format(what),
								   response['error']['code'],
						           response['error']['message'])
		return response

	@overrides
	def post(self, endpoint, data=None):
		url = '{0}/{1}'.format(self.api, endpoint)
		headers = {'content-type': 'application/json'}
		response = requests.post(url,
							 params=self.parameters,
							 data=json.dumps(data),
							 headers=headers)
		return response
