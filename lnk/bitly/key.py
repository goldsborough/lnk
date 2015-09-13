#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import beauty
import config
import errors

from bitly.command import Command

CLIENT_ID = '049118cdcf01c6b267f77582990d48da9127259a'
CLIENT_SECRET = 'b5257382fd1c7118688cae7942d5128b4d995c9e'

def echo(*args):
	click.echo(Key().fetch(*args), nl=False)

class Key(Command):

	def __init__(self, raw=False):
		super(Key, self).__init__('key')
		self.raw = raw
		self.parameters['client_id'] = CLIENT_ID
		self.parameters['client_service'] = CLIENT_SECRET

	def fetch(self, _, login, password, show):
		key = self.request(login, password)
		print(key)
		with config.Manager('bitly', write=True) as manager:
			manager['key'] = key

		if show:
			output = key if self.raw else beauty.boxify([[key]])
			return output + '\n'
		return ''

	def request(self, login, password):
		response = self.post(self.endpoints['oauth'],
							 authorization=(login, password))
		print(response)
		return self.verify(response, 'generate an API key')

	@staticmethod
	def verify(response, what):
		if not str(response.status_code).startswith('2'):
			raise errors.HTTPError('Could not {}.'.format(what),
								   response.status_code,
						           response.reason)
		return response.text