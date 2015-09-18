#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Link shortening and expansion for the tinyurl client."""

import click
import ecstasy
import pyperclip
import re

import lnk.beauty
import lnk.errors

from lnk.tinyurl.command import Command

def echo(*args):
	"""
	Executes a link command and echoes its output.

	Arguments:
		args (variadic): The arguments to pass to an
						 Link instance's fetch() method.
	"""
	click.echo(Link().fetch(*args))

class Link(Command):
	"""
	Class to shorten or expand a url using tinyurl.

	This class can shorten a long url to a shortened tinyurl url.

	Attributes:
		raw (bool): Whether to prettify the output or
					return it raw, for internal use.
		already_copied (bool): Flag set the first time a url is copied
							   to the clipboard, such that only the first
							   is copied.
		http (regex): A compiled regular-expression object matching a
					  HTTP(S) protocol, for URL-checking.
	"""
	def __init__(self, raw=False):
		super(Link, self).__init__('link')
		self.raw = raw
		self.already_copied = False
		self.http = re.compile(r'https?://')

	def fetch(self, copy, quiet, urls, pretty):
		"""
		Fetches a short or expanded link.

		Arguments:
			copy (bool): Whether or not to copy the first shortened or
						 expanded link to the clipboard.
			quiet (bool): Whether or not to swallow warnings about urls
						  having to be modified because they do not have
						  a protocol specified (i.e. no 'http://').
			urls (tuple): A tuple of long urls to shorten.
			pretty (bool): Whether or not to make the output pretty (in a box).

		Returns:
			A raw list of lines for other internal use if self.raw is True,
			else a pretty list in a box if pretty is True, else the same
			list as in the first case, but joined to a string for output.
		"""
		result = []
		threads = []
		for url in urls:
			t = self.new_thread(self.shorten, result, copy, quiet, pretty, url)
			threads.append(t)
		self.join(threads)

		if self.raw:
			return result
		return lnk.beauty.boxify([result]) if pretty else '\n'.join(result)

	def shorten(self, result, copy, quiet, pretty, url):
		"""
		Shortens a long url.

		Arguments:
			result (list): The list to which to append the shortened url.
			copy (bool): Whether or not to copy the first url to the clipboard.
			quiet (bool): Whether or not to swallow warnings about urls
						  having to be modified because they do not have
						  a protocol specified (i.e. no 'http://').
			pretty (bool): Whether or not to make the url pretty. If yes,
						   the formatted string appended to the result list
						   follows the schema '<long> => <url>'.
			urls (tuple): The tuple of long urls to shorten.
		"""
		if not self.http.match(url):
			url = 'http://{0}'.format(url)
			if not quiet:
				lnk.errors.warn("Prepending 'http://' to '{0}'".format(url))
		short = self.request(url)
		formatted = self.copy(copy, short)
		if pretty:
			formatted = '{0} => {1}'.format(url, formatted)
		with self.lock:
			result.append(formatted)

	def request(self, url):
		"""
		Requests and returns a short url for a long one.

		Arguments:
			url (str): The long url to shorten.

		Returns:
			The shortened link.
		"""
		response = self.get(self.endpoints['create'], dict(url=url))
		response = self.verify(response, "shorten url '{0}'".format(url))

		return response['shorturl']

	def copy(self, copy, url):
		"""
		Copies a url to the clipboard if possible.

		"If possible" means the url is only copied if no other url
		has so-far been copied to the clipboard during the same
		fetch() call, and also only if the 'copy' is set. If the url
		is copied, it is formatted using ecstasy to make it bold.

		Arguments:
			copy (bool): Whether or not to allow copying
						 to the clipboard at all.
			url (str): The url to (possibly) copy.

		Returns:
			The original url if the 'copy' flag is unset or another link
			has already been copied to the clipboard during the same call
			to fetch(), else the url, formatted with ecstasy to appear bold
			in the terminal.
		"""
		if copy and not self.already_copied:
			self.already_copied = True
			pyperclip.copy(url)
			url = ecstasy.beautify('<{0}>'.format(url), ecstasy.Style.Bold)

		return url
