#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import config
import errors

from abstract import AbstractCommand

class Command(AbstractCommand):
	def __init__(self, which):
		super(Command, self).__init__('tinyurl', which)
		with config.Manager('tinyurl') as manager:
			self.parameters = {'apikey': manager['key']}
		self.parameters['format'] = 'json'
		self.parameters['provider'] = 'tinyurl_com'

	@staticmethod
	def verify(response, what):
		if not str(response.status_code).startswith('2'):
			raise errors.HTTPError('Could not {0}!'.format(what),
								   response.status_code,
						           response.reason)
		data = response.json()
		if data['state'] == 'error':
			what = 'Could not {0}!'.format(what)
			raise errors.APIError(what)

		return data