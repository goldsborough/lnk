#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import errors
import config

from googl.command import Command

CLIENT_ID = '324510822959-0guqfe402t3drn0bkbj8jia65n5e36vp.apps.googleusercontent.com'
CLIENT_SECRET = 'l-u_cChvb1reWscds0_zTsba'

def echo(*args):
	click.echo(Key().fetch(*args), nl=False)

class Key(Command):

	def __init__(self, raw=False):
		super(Key, self).__init__('key')
		self.raw = raw

	def fetch(self, _, login, password, show):
		key = self.request(login, password)
		with config.Manager('bitly', write=True) as manager:
			manager['key'] = key

		if show:
			output = key if self.raw else self.boxify([[key]])
			return output + '\n'
		return ''

	def request(self, login, password):
		response = self.post(self.endpoints['oauth'],
							 authorization=(login, password))
		return self.verify(response, 'generate API key')

	@staticmethod
	def verify(response, what):
		if not str(response.status_code).startswith('2'):
			raise errors.HTTPError('Could not {}.'.format(what),
								   response.status_code,
						           response.reason)
		return response.text