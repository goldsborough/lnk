#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import Queue
import re
import requests
import threading
import sys

import config
import errors

from collections import namedtuple

class AbstractCommand(object):

	def __init__(self, service, command):
		with config.Manager(service) as manager:
			self.url = manager['url']
			self.api = '{0}/v{1}'.format(self.url, manager['version'])
			self.config = manager['commands'][command]
			self.endpoints = self.config['endpoints']
			self.settings = self.config.get('settings')
			self.sets = self.config.get('sets')
		self.http = re.compile(r'https?://')	
		self.queue = Queue.Queue()
		self.lock = threading.Lock()
		self.error = None

	def fetch(self, *args):
		raise NotImplementedError

	def get(self, endpoint, parameters=None):
		url = '{0}/{1}'.format(self.api, endpoint)
		if not parameters:
			parameters = self.parameters
		else:
			parameters.update(self.parameters)

		return requests.get(url, params=parameters)

	def post(self, endpoint, authorization=None, data=None):
		url = '{0}/{1}'.format(self.url, endpoint)
		return requests.post(url, auth=authorization, data=data)

	def new_thread(self, function, *args, **kwargs):
		def proxy(*args, **kwargs):
			try:
				function(*args, **kwargs)
			except Exception:
				_, self.error, _ = sys.exc_info()
		thread = threading.Thread(target=proxy, args=args, kwargs=kwargs)
		thread.daemon = True
		thread.start()
		return thread

	def join(self, threads, timeout=10):
		for thread in threads:
			thread.join(timeout=timeout)
		if self.error:
			raise self.error

	@staticmethod
	def verify(response, what):
		raise NotImplementedError

	@staticmethod
	def boxify(results):
		results, width = AbstractCommand.get_escaped(results)

		border = width + 2
		lines = ['┌{0}┐'.format('─' * border)]

		for n, result in enumerate(results):
			for line in result:
				adjusted = AbstractCommand.ljust(line, width)
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
		pattern = re.compile(r'^(.*)'    			# anything
						     r'(?:\033\[[\d;]+m)'   # escape codes
						     r'(.+)'			 	# formatted string
						     r'(?:\033\[[\d;]+m)'   # escape codes
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
