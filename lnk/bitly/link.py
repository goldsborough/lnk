#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Link shortening and expansion for the bit.ly client."""

import click
import ecstasy
import pyperclip
import re

import lnk.beauty
import lnk.errors

from lnk.bitly.command import Command

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
	Class to shorten or expand a url using bit.ly.

	This class can shorten a long url to a shortened bit.ly url,
	or expand a shortened bit.ly url to its original long url.

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

	def fetch(self, copy, quiet, expand, shorten, pretty):
		"""
		Fetches a short or expanded link.

		Arguments:
			copy (bool): Whether or not to copy the first shortened or
						 expanded link to the clipboard.
			quiet (bool): Whether or not to swallow warnings about urls
						  having to be modified because they do not have
						  a protocol specified (i.e. no 'http://').
			expand (tuple): A tuple of short urls to expand.
			shorten (tuple): A tuple of long urls to shorten.
			pretty (bool): Whether or not to make the output pretty (in a box).

		Returns:
			A raw list of lines for other internal use if self.raw is True,
			else a pretty list in a box if pretty is True, else the same
			list as in the first case, but joined to a string for output.
		"""
		self.already_copied = False
		result = self.shorten_urls(copy, quiet, shorten)
		result += self.expand_urls(copy, expand)

		if self.raw:
			return result
		return lnk.beauty.boxify([result]) if pretty else '\n'.join(result)

	def shorten_urls(self, copy, quiet, urls):
		"""
		Shortens a sequence of long urls.

		Arguments:
			copy (bool): Whether or not to copy the first url to the clipboard.
			quiet (bool): Whether or not to swallow warnings about urls
						  having to be modified because they do not have
						  a protocol specified (i.e. no 'http://').
			urls (tuple): The tuple of long urls to shorten.

		Returns:
			A list of lines for output.
		"""
		lines = []
		threads = []
		for url in urls:
			if not self.http.match(url):
				url = 'http://{0}'.format(url)
				if not quiet:
					lnk.errors.warn("Prepending 'http://' to '{0}'".format(url))
			self.queue.put(url)
			threads.append(self.new_thread(self.shorten, lines, copy))
		self.join(threads)
		return lines

	def expand_urls(self, copy, urls):
		"""
		Expands a sequence of short urls.

		Arguments:
			copy (bool): Whether or not to copy the first url to the clipboard.
			urls (tuple): The tuple of short urls to expand.

		Returns:
			A list of lines for output.
		"""
		lines = []
		threads = []
		for url in urls:
			self.queue.put(url)
			threads.append(self.new_thread(self.expand, lines, copy))
		self.join(threads)

		return lines

	def shorten(self, lines, copy):
		"""
		Requests a shortend link and appends it to a given list.

		A shortened link is retrieved via get_short(), then (possibly)
		copied to the clipboard via copy(), then appended to the given
		list in a thread-safe (locked) way.

		Arguments:
			lines (list): The list of lines to append the url to.
			copy (bool): Whether or not to copy the link to the clipboard
						 (if no other link has already been copied).
		"""
		url = self.queue.get()
		short = self.get_short(url)
		formatted = self.copy(copy, short)
		with self.lock:
			lines.append('{0} => {1}'.format(url, formatted))

	def expand(self, lines, copy):
		"""
		Requests an expanded link and appends it to a given list.

		An expanded link is retrieved via get_long(), then (possibly)
		copied to the clipboard via copy(), then appended to the given
		list in a thread-safe (locked) way.

		Arguments:
			lines (list): The list of lines to append the url to.
			copy (bool): Whether or not to copy the link to the clipboard
						 (if no other link has already been copied).
		"""
		url = self.queue.get()
		expanded = self.get_long(url)
		formatted = self.copy(copy, expanded)
		with self.lock:
			lines.append('{0} => {1}'.format(url, formatted))

	def get_short(self, url):
		"""
		Requests and returns a short url for a long one.

		Arguments:
			url (str): The long url to shorten.

		Returns:
			The shortened link.
		"""
		response = self.get(self.endpoints['shorten'], dict(longUrl=url))
		response = self.verify(response, "shorten url '{0}'".format(url))
		
		return response['url']

	def get_long(self, url):
		"""
		Requests and returns an expanded url for a short one.

		Arguments:
			url (str): The short bit.ly link (bitlink) to expand.

		Returns:
			The expanded link.
		"""
		response = self.get(self.endpoints['expand'], dict(shortUrl=url))
		response = self.verify(response,
							   "expand url '{0}'".format(url),
							   'expand')

		return response['long_url']

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
