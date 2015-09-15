#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from overrides import overrides

import config
import errors

from abstract import AbstractCommand

class Command(AbstractCommand):
	def __init__(self, which):
		super(Command, self).__init__('bitly', which)
		with config.Manager('bitly') as manager:
			if not manager['key'] and which != 'key':
				raise errors.AuthorizationError('bitly')
			self.parameters = {'access_token': manager['key']}

	@staticmethod
	@overrides
	def verify(response, what, inner=None):
		if not str(response.status_code).startswith('2'):
			raise errors.HTTPError('Could not {0}!'.format(what),
								   response.status_code,
						           response.reason)
		response = response.json()
		if not str(response['status_code']).startswith('2'):
			raise errors.HTTPError('Could not {0}!'.format(what),
								   response['status_code'],
						           response['status_txt'])
		data = response['data']
		if inner:
			data = data[inner][0]
		if 'error' in data:
			what = 'Could not {0}!'.format(what)
			raise errors.APIError(what, data['error'])

		return data

def filter_sets(all_sets, only, hide):
	if only:
		sets = {k:v for k, v in all_sets.items() if k in only}
	else:
		sets = all_sets.copy()
	for key in hide:
		if key in sets:
			del sets[key]

	return sets
