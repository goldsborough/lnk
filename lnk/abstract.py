#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Includes the base-class for all commands of any service."""

from __future__ import unicode_literals

import ecstasy
import requests
import threading
import sys

try:
	from Queue import Queue
except ImportError:
	from queue import Queue

import lnk.config
import lnk.errors

class AbstractCommand(object):
	"""
	Abstract-base-class for all commands of any service.

	This class' constructor handles the bulk of configuration every
	command needs, such as fetching the service's API url, available
	endpoints and default settings. It also gives each command a queue
	and lock for threading, as well as a few other things most, if not
	all, commands need. The class defines an interface all commands must
	have, with some of AbstractCommand's methods, such as fetch(), not
	being implemented and throwing a NotImplementedError if called directly.
	An AbstractCommand must have knowledge about the service that the class
	subclassing it uses (e.g. bit.ly or tinyurl), as well as about the
	name of the command (e.g. 'link' or 'stats').

	Attributes:
		url (str): The URL of the API.
		api (str): The URL of the API, joined with its version. Endpoints can
				   be joined to this string to form a full URL (without
				   parameters) for a request.
		config (dict): The configuration data of a command.
		endpoints (dict): The endpoints for a command.
		settings (dict): The default settings of a command.
		sets (dict|None): If available, the data sets/categories that the
						  command allows, else None if the command has no
						  such thing (e.g. the 'link' command).
		queue (Queue.Queue): A queue for thread-safe data-passing.
		lock (threading.Lock): A lock object for thread-safe actions.
		error (Exception): The last exception thrown by a thread started
						   with the new_thread method. This is useful to
						   see if a thread threw an exception which would
						   otherwise not be properly handled (because you
						   can't catch exceptions from a child-thread in the
						   main thread).
		parameters (dict): Dictionary for the parameters of an HTTP request.
		list_item (str): A string, formatted with ecstasy, that should be used
						 to format a list-item (e.g. for the stats command).
						 It already includes the necessary markup such that
						 str.format() can be used on it directly with the
						 string to be formatted.
	"""
	def __init__(self, service, command):
		with lnk.config.Manager(service) as manager:
			self.url = manager['url']
			self.api = '{0}/v{1}'.format(self.url, manager['version'])
			self.config = manager['commands'][command]
			self.endpoints = self.config['endpoints']
			self.settings = self.config.get('settings')
			self.sets = self.config.get('sets')
		self.queue = Queue()
		self.lock = threading.Lock()
		self.error = None
		self.parameters = {}
		self.list_item = ecstasy.beautify(' <+> {0}', ecstasy.Color.Red)

	def fetch(self, *args):
		"""
		Abstract method to fetch command-specific data.

		Arguments:
			args (variadic): Whatever arguments the overriden method takes.

		Raises:
			NotImplementedError: When called directly.
		"""
		raise NotImplementedError

	def get(self, endpoint, parameters=None):
		"""
		Base method to perform an HTTP request with the GET method.

		Arguments:
			endpoint (str): The endpoint at which to request data.
			parameters (dict): Additional parameters to pass with the request.

		Return:
			The requests.Response object resulting from the request.
		"""
		url = '{0}/{1}'.format(self.api, endpoint)
		if not parameters:
			parameters = self.parameters
		else:
			parameters.update(self.parameters)

		return requests.get(url, params=parameters, timeout=60)

	def post(self, endpoint, authorization=None, data=None):
		"""
		Base method to perform an HTTP request with the POST method.

		Arguments:
			endpoint (str): The endpoint at which to send data.
			authorization (tuple): Optionally, a (login, password) tuple that
								   should be used for HTTP authorization.
			data (dict): Optionally, data to send with the request.

		Return:
			The requests.Response object resulting from the request.
		"""
		url = '{0}/{1}'.format(self.url, endpoint)

		return requests.post(url, auth=authorization, data=data, timeout=60)

	def new_thread(self, function, *args, **kwargs):
		"""
		Runs a function in a new thread and returns the thread.

		The function is run in a new thread in way that all positional
		and keyword arguments can be forwarded to the function. Additionally,
		extra measures are taken to wrap the function into another proxy
		function that handles exceptions which would otherwise not be handled.
		If the function to be called throws an exception, this is recorded
		and the exception is assigned to 'error' attribute, where it can later
		be checked.

		Arguments:
			function (func): The function to execute.
			args (variadic): The positional arguments to pass to the function
							 when calling it.
			kwargs (variadic): The keyword arguments to pass to the function
							   when calling it.

		Returns:
			The started (!) thread in which the function is being executed.
		"""
		def proxy(*args, **kwargs):
			"""Proxy function for concurrent exception-handling."""
			try:
				function(*args, **kwargs)
			except Exception:
				_, self.error, _ = sys.exc_info()
		thread = threading.Thread(target=proxy, args=args, kwargs=kwargs)
		thread.daemon = True
		thread.start()

		return thread

	def join(self, threads, timeout=120):
		"""
		Joins a list of thread and checks for errors.

		Each thread is join with a timeout period as specified by the timeout
		parameter of this function. If an error was found in the 'error'
		attribute, it is re-raised so that it can be caught in the main thread.

		Arguments:
			threads (list): The list of threading.Threads to join.
			timeout (float): A floating-point number specifying the number of
							 seconds to wait when joining. Defaults to 60
							 seconds.

		Raises:
			lnk.errors.InternalError: If a thread could not be joined in the given
								  timeout period (i.e. if it is still alive after
								  joining).
			Other errors: If a thread threw an exception, this exception is
						  re-raised in the main thread.
		"""
		for thread in threads:
			thread.join(timeout=timeout)
			if thread.is_alive():
				raise lnk.errors.InternalError('Could not join thread.')
		if self.error:
			raise self.error

def filter_sets(all_sets, only, hide):
	"""
	Filters a set of categories.

	This method is used by many commands that use some sort of dictionary
	of available data sets/categories, which must filter those sets according
	to the ones the user wants to have included in the response by that command.

	Arguments:
		all_sets (dict): The base dictionary of all available sets (from which
						 a subset should be filtered).
		only (tuple): A tuple of the names of the categories/sets to include.
		hide (tuple): A tuple of the names of the categories/sets to exclude.
					  Note that sets are hidden after the 'only' sets have
					  been processed, i.e. if a certain set is in 'only' and
					  in 'hide', it will first be selected and then discared
					  again (which would make no sense). Usually either 'only'
					  or 'hide' is empty.

	Returns:
		A dictionary containing the filtered key/value pairs.
	"""
	filtered = {}
	only = only or all_sets
	for key, value in all_sets.items():
		if key in only and key not in hide:
			filtered[key] = value

	return filtered
