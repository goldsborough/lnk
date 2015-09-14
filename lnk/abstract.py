#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ecstasy
import Queue
import re
import requests
import threading
import sys

import config

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
		self.parameters = {}
		self.list_item = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)

	def fetch(self, *args):
		raise NotImplementedError

	def get(self, endpoint, parameters=None):
		url = '{0}/{1}'.format(self.api, endpoint)
		if not parameters:
			parameters = self.parameters
		else:
			parameters.update(self.parameters)

		return requests.get(url, params=parameters, timeout=60)

	def post(self, endpoint, authorization=None, data=None):
		url = '{0}/{1}'.format(self.url, endpoint)

		return requests.post(url,
							 auth=authorization,
							 data=data,
							 timeout=60)

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
