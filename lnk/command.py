#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import requests

import config
import errors

from collections import namedtuple

class Command(object):

	def __init__(self, service, command):
		with config.Manager(service) as manager:
			self.url = manager['url'] + 'v{0}'.format(manager['version'])
			self.config = manager['commands'][command]
			self.endpoints = self.config['endpoints']
			self.defaults = self.config.get('defaults')
			self.parameters = {'access_token': manager['key']}
			self.http = re.compile(r'https?://')

	def fetch(self, *args):
		raise NotImplementedError

	def request(self, endpoint):
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

	@staticmethod
	def boxify(results):
		results, width = Command.get_escaped(results)

		border = width + 2
		lines = ['┌{0}┐'.format('─' * border)]

		for n, result in enumerate(results):
			for line in result:
				adjusted = Command.ljust(line, width)
				lines.append('│ {0} │'.format(adjusted))
			if n + 1 < len(results):
				lines.append('├{0}┤'.format('─' * border))

		lines += ['└{0}┘'.format('─' * border)]

		return '\n'.join(lines)

	@staticmethod
	def ljust(line, width):
		return line.raw + ' ' * (width - len(line.escaped))

	@staticmethod
	def get_escaped(results):
		pattern = re.compile(r'^(\s*[-+*]\s*)?'    		# list bullet
							      r'(?:\033\[[\d;]+m)?' # escape codes
							      r'([\s\w]+)'				# formatted string
							      r'(?:\033\[[\d;]+m)?' # escape codes
							      r'(.*)$')				# anything

		Line = namedtuple('Line', ['raw', 'escaped'])
		width = 0
		mapped = []
		for result in results:
			lines = []
			for line in result:
				escaped = line
				if '\033' in line:
					match = pattern.search(line)
					escaped = ''.join([i for i in match.groups() if i])
				if len(escaped) > width:
					width = len(escaped)
				lines.append(Line(line, escaped))
			mapped.append(lines)

		return mapped, width
