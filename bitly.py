#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import argparse
import requests

import errors
from errors import Error, HTTPError, APIError

def handle(args):

	if "stats" in args:
		stats = Stats()
		return stats.parse(args)

	elif "info" in args:
		info = Info()
		return info.parse(args)
	else:
		link = Link()
		return link.parse(args)
 
class Command:
	def __init__(self, name):

		with open("config.json") as file:
			config = json.loads(file.read())["bitly"]



		self.api = config["api"] + "v{}".format(config["version"])

		self.key = config["key"]

		self.config = config["commands"][name]

	def parse(self):
		pass

	def request(self, endpoint, parameters):

		parameters["access_token"] = self.key

		response = requests.get("{}/{}".format(self.api, endpoint),
							    params=parameters)

		return response.json()

	def check(self, response, what, sub=None):

		if not str(response["status_code"]).startswith('2'):
			raise HTTPError("Sorry, could not {}.".format(what),
						    response["status_code"],
				            response["status_txt"])

		data = response["data"]

		if sub:
			data = data[sub][0]

		if "error" in data:
			raise APIError("Sorry, could not {}.".format(what),
			                data["error"])

class Link(Command):
	def __init__(self):

		super().__init__("link")

		self.parser = argparse.ArgumentParser()

		self.parser.add_argument("-e",
						  "--expand",
						  action="store_true")

		self.parser.add_argument("url")

		self.http = re.compile(r"http(s?)://")

	def parse(self, args):

		args = self.parser.parse_args(args)

		if args.expand:
			return self.expand(args.url)

		else:
			return self.shorten(args.url)

	def shorten(self, url):

		if not self.http.match(url):
			errors.warn("Prepending http://")
			url = "http://" + url

		response = self.request(self.config["endpoints"]["shorten"],
					     		{
					     			"longUrl": url
					     		})

		self.check(response, "shorten url")

		return response['data']['url']

	def expand(self, url):

		response = self.request(self.config["endpoints"]["expand"],
							    {
							    	"shortUrl": url
							    })

		self.check(response, "expand url", "expand")

		return response['data']['expand'][0]['long_url']

"""

		config = self.commands["stats"]

		stats = subparsers.add_parser("stats")

		stats.set_defaults(handle=self.stats)

		stats.add_argument("-o",
						   "--only",
						   choices=config["sets"])

		stats.add_argument("-u",
						   "--unit",
						   choices=config["unit"],
						   default=config["defaults"]["unit"])

		stats.add_argument("-t",
						   "--time",
						   type=int)

		stats.add_argument("-l",
						   "--limit",
						   type=int,
						   default=config["defaults"]["limit"])

		stats.add_argument("url")

	def stats(self, args):

		parameters = {
						"link": args.url,
						"limit": args.limit
					 }

		endpoints = self.commands["stats"]["endpoints"]

		# Restrict the data retrieved
		if args.only:
			endpoints = [endpoints[args.only]]

		if args.unit != "infinity":
			parameters["unit"] = args.unit

			if args.time:
				parameters["unit"] = args.time

		# short stats -o clicks -u all -u month 4 

		#response = line = chr(0x2500) * 10 + "\n"

		stats = [ ]

		for name, endpoint in endpoints.items():

			response = self.request(endpoint, parameters)

			self.check(resposnse, "retreive " + name)

			lines = [ ]

			if name == "clicks":
				lines.append((name, response['data']['link_clicksclicks']))



		return response


"""