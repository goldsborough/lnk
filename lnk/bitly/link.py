#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import errors

from command import Command

class Link(Command):
	def __init__(self, args):

		super(Link, self).__init__("link")

		self.parser = argparse.ArgumentParser()

		self.parser.add_argument("-e",
						  		 "--expand",
						  		 action="append")

		self.parser.add_argument("shorten", nargs="*")

		self.parse(args)

	def parse(self, args):

		args = self.parser.parse_args(args)

		result = ""

		if args.expand:

			for url in args.expand:
				result += "{} -> {}\n".format(url, self.expand(url))

			del self.parameters["shortUrl"]

		for url in args.shorten:

			if not self.http.match(url):
				errors.warn("Prepending 'http://' to " + url)
				url = "http://" + url

			result += "{} -> {}\n".format(url, self.shorten(url))			

		return result.rstrip()

	def shorten(self, url):

		self.parameters["longUrl"] = url

		response = self.request(self.config["endpoints"]["shorten"])

		self.verify(response, "shorten url")

		return response['data']['url']

	def expand(self, url):

		self.parameters["shortUrl"] = url

		response = self.request(self.config["endpoints"]["expand"])

		self.verify(response, "expand url", "expand")

		return response['data']['expand'][0]['long_url']