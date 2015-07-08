#!/usr/local/bin/python3

import errors
import json
import argparse
import requests

def handle(args):

	bitly = Bitly()

	return bitly.parse(args)

class Bitly:

	def __init__(self):

		config = { }

		with open("config.json") as file:
			config = json.loads(file.read())["services"]["bitly"]

		self.api = config["api"] + "v{}".format(config["version"])

		self.key = config["key"]

		self.commands = config["commands"]


		self.parser = argparse.ArgumentParser()

		subparsers = self.parser.add_subparsers()


		link = subparsers.add_parser("link")

		link.set_defaults(handle=self.link)

		link.add_argument("-e",
						  "--expand",
						  action="store_true")

		link.add_argument("url")


		stats = subparsers.add_parser("stats")

		#stats.set_defaults(handle=self.stats)

		stats.add_argument("-o",
						   "--only",
						   choices=config["commands"]["stats"]["sets"])

		stats.add_argument("-u",
						   "--unit",
						   choices=config["commands"]["stats"]["units"])

		stats.add_argument("-r",
						   "--restrict",
						   type=int)

		stats.add_argument("url")

	def parse(self, args):

		if args[0] not in self.commands:
			args.insert(0, "link")

		command = self.parser.parse_args(args)

		return command.handle(command)

	def request(self, endpoint, parameters):

		parameters["access_token"] = self.key

		response = requests.get("{}/{}".format(self.api, endpoint),
							    params=parameters)

		# Decode the UTF-8 bytearray
		return response.json()

	def check(self, response, what=""):

		if not str(response["status_code"]).startswith('2'):
			raise errors.APIError("Sorry, could not {}".format(what),
								  response["status_code"],
								  response["status_txt"])

	def link(self, args):

		if args.expand:
			return self.expand(args.url)

		else:
			return self.shorten(args.url)

	def shorten(self, url):

		response = self.request(self.commands["link"]["endpoints"]["shorten"],
					     		{"longUrl": url})

		self.check(response, "shorten url")

		return response['data']['url']

	def expand(self, url):

		response = self.request(self.commands["link"]["endpoints"]["expand"],
							    {"shortUrl": url})

		self.check(response, "expand url")

		return response['data']['url']