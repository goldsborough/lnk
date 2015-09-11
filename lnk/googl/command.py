#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import config
import errors

from abstract import AbstractCommand

class Command(AbstractCommand):
	def __init__(self, which):
		super(Command, self).__init__('googl', which)
		with config.Manager('googl') as manager:
			self.parameters = {'access_token': manager['key']}

	@staticmethod
	def verify(response, what):
		response = response.json()
		if 'error' in response:
			raise errors.HTTPError('Could not {0}.'.format(what),
								   response['error']['code'],
						           response['error']['message'])
		elif response['status'] == 'MALWARE':
			errors.warn("goo.gl believes the url '{0}' is malware"
						"!".format(response['longUrl']))

		return data