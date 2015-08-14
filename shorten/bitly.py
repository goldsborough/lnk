#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import math
import argparse
import requests

from pycountry import countries

import errors
import beautifier

def handle(args):

	if "stats" in args:
		return Stats().parse(args[1:])

	elif "info" in args:
		return Info().parse(args[1:])

	else:
		return Link().parse(args)
 
class Command(object):
	def __init__(self, command):

		with open("../config/config.json") as file:
			config = json.loads(file.read())["bitly"]

		self.api = config["api"] + "v{}".format(config["version"])

		self.config = config["commands"][command]

		self.parameters = {"access_token": config["key"]}

	def parse(self):
		pass

	def request(self, endpoint):

		response = requests.get("{}/{}".format(self.api, endpoint),
							    params=self.parameters)

		return response.json()

	def check(self, response, what, sub=None):

		if not str(response["status_code"]).startswith('2'):
			raise errors.HTTPError("Could not {}.".format(what),
						    response["status_code"],
				            response["status_txt"])

		data = response["data"][sub][0] if sub else response["data"]

		if "error" in data:
			raise errors.APIError("Could not {}.".format(what),
			                	  data["error"])

class Link(Command):
	def __init__(self):

		super(Link, self).__init__("link")

		self.parser = argparse.ArgumentParser()

		self.parser.add_argument("-e",
						  		 "--expand",
						  		 action="append")

		self.parser.add_argument("shorten", nargs="*")

		self.http = re.compile(r"http(s?)://")

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

		self.check(response, "shorten url")

		return response['data']['url']

	def expand(self, url):

		self.parameters["shortUrl"] = url

		response = self.request(self.config["endpoints"]["expand"])

		self.check(response, "expand url", "expand")

		return response['data']['expand'][0]['long_url']

class Stats(Command):
	def __init__(self):

		super().__init__("stats")

		self.parser = argparse.ArgumentParser(prog="short stats",
										      conflict_handler="resolve")

		self.parser.add_argument("-o",
					   			 "--only",
					   		 	 action="append",
					   			 choices=self.config["sets"])

		self.parser.add_argument("-h",
								 "--hide",
	 							 action="append",
	 							 choices=self.config["sets"])

		self.parser.add_argument("-a",
							     "--all",
							     action="store_true")

		units = ", ".join(self.config["units"])

		self.parser.add_argument("-t",
							     "--time",
							     action="append",
							     nargs=2,
							     metavar=("integer", "{{{}}}".format(units)))

		self.parser.add_argument("-l",
								 "--limit",
								 type=int,
								 default=self.config["defaults"]["limit"])

		self.parser.add_argument("-i",
								 "--info",
								 action="store_true")

		# {{}} to escape curly braces, {{{}}}
		# to format something in curly braces 

		self.parser.add_argument("urls", nargs='+')

		self.parameters["timezone"] = int(time.timezone / 3600)

	def parse(self, args):

		args = self.parser.parse_args(args)

		self.parameters["limit"] = args.limit

		endpoints = args.only if args.only else self.config["sets"]

		if args.hide:
			for i in args.hide:
				endpoints.remove(i)

		time = args.time

		if not time:
			# 'day' is Bitly's default unit. The important part
			# is to set the time span to -1, that retrieves
			# all data for all time units (since forever)
			time = [(-1, "days")]

		else:
			for n, (span, unit) in enumerate(time):

				try:
					span = int(span)

				except ValueError:
					raise errors.ParseError("'{}' ".format(span) +
											"is not a valid"     +
						  					"time span (integer)!")

				if unit not in self.config["units"]:
					units = ", ".join(self.config["units"])
					raise errors.ParseError("'{}' ".format(unit)   +
									        "is not a valid time " +
									        "unit ({})!".format(units))

				if unit == "minute" and span > 60:
						raise errors.Error("'{}'".format(span) +
										   "exceeds maximum of 60 minutes!")

				time[n] = (span, unit)

		stats = [ ]

		self.info = [ ]

		if args.info:
			info = Info()

		for url in args.urls:

			single = {  
				"url" : url,
				"info" : None
			}

			if args.info:
				single["info"] = info.parse([url], False)[0]

			single["data"] = self.retrieve(url, time, endpoints)

			stats.append(single)

		stats = self.preprocess(stats)

		return beautifier.beautify(stats)

	def retrieve(self, url, time, endpoints):

		stats = [ ]

		self.parameters["link"] = url

		for endpoint in endpoints:

			result = {
				"type": endpoint,
				"times": [ ]
			}

			for span, unit in time:

				timepoint = {
					"span" :  span,
					"unit": unit
				}

				l# Get rid of the extra s in e.g. "weeks"
				self.parameters["unit"] = unit[:-1]

				self.parameters["units"] = span

				response = self.request(self.config["endpoints"][endpoint])

				self.check(response, "retrieve {} for {}".format(endpoint, url))

				# clicks is the only one where the data
				# retrieved has a different name than its endpoint
				e = endpoint if endpoint != "clicks" else "link_clicks"

				timepoint["data"] = response["data"][e]

				result["times"].append(timepoint)

			stats.append(result)

		return stats

	def preprocess(self, stats):

		statistics = {
			"data": "statistics",
			"sub": []
		}

		maxWidth = lambda d: len(max(d,key=len) + 
						    	 max(map(str,d.values()),key=len))

		for url in stats:

			box = {"data" : { "url" : url["url"] }}

			if url["info"]:
				box["data"].update(url["info"])

			urlbox = [box]

			for data in url["data"]:

				box = { "data": data["type"] }

				if data["type"] != "clicks":
					urlbox.append(box)
					box["sub"] = [ ]

				else:
					urlbox.append(box.copy())
					box = { "data" : { } }
					urlbox.append(box)

				for timepoint in data["times"]:

					if timepoint["span"] == -1:
						time = "Total"
					else:
						time = "Last {} {}".format(timepoint["span"],
											   	   timepoint["unit"])

					if data["type"] == "clicks":
						box["data"][time] = timepoint["data"]
					else:

						sub = [ ] if time == "Total" else [{"data": time}]

						if not timepoint["data"]:
							sub.append({"data": "None"})

						# For each item, e.g. country + clicks
						for item in timepoint["data"]:

							if data["type"] == "countries":
								# Convert short ISO name (e.g. US)
								# to full name (e.g. United States)
								country = countries.get(alpha2=item["country"])
								item["country"] = country.name

							sub.append({"data" : item})

						box["sub"].append(sub)

			statistics["sub"].append(urlbox)

		return statistics

class Info(Command):
	def __init__(self):

		super().__init__("info")

		self.parser = argparse.ArgumentParser("short info",
											  conflict_handler="resolve")

		self.parser.add_argument("-o",
					   			 "--only",
					   		 	 action="append",
					   			 choices=self.config["sets"])

		self.parser.add_argument("-h",
								 "--hide",
	 							 action="append",
	 							 choices=self.config["sets"])

		self.parser.add_argument("urls", nargs="+")

	def parse(self, args, beauty=True):

		args = self.parser.parse_args(args)

		sets = args.only if args.only else self.config["sets"].keys()

		if args.hide:
			for i in args.hide:
				sets.remove(i)

		sets = [self.config["sets"][key] for key in sets]

		info = [ ]

		for url in args.urls:

			result = self.retrieve(url, sets)

			mapped = { }

			# Reverse map
			for i, j in result.items():
				for k, l in self.config["sets"].items():
					if i == l:
						if k == "created":
							# UNIX timestamp to string
							j = time.ctime(j)
						elif k == "user" and not j:
							j = "Not public"
						mapped[k] = j  

			mapped["url"] = url

			info.append(mapped)

		return info if not beauty else self.beautify(info)

	def retrieve(self, url, sets):

		self.parameters["shortUrl"] = url

		response = self.request(self.config["endpoints"]["info"])

		self.check(response,
				   "retrieve information for " + url,
				   "info")

		response = response["data"]["info"][0]

		return {i : response[i] for i in response if i in sets}

	def beautify(self, info):

		boxes = [ ]

		width = 0

		for i in info:

			keyWidth = len(max(i.keys(), key=len)) + 1

			valueWidth = len(max(map(str, i.values()), key=len))

			# The horizontal bar of only - (dash-like) characters 
			horizontal = chr(0x2500) * (keyWidth + valueWidth + 3)

			if len(horizontal) + 2 > width:
				width = len(horizontal) + 2

			lines = [chr(0x250C) + horizontal + chr(0x2510)]

			for key, value in i.items():

				key = (key + ":").ljust(keyWidth).title()

				value = str(value).ljust(valueWidth)

				lines.append("{0} {1} {2} {0}".format(chr(0x2502), key, value))

			lines.append(chr(0x2514) + horizontal + chr(0x2518))

			boxes.append(lines)

		# See when we need to wrap the boxes
		wrap = int(os.get_terminal_size().columns / width)

		beauty = ""

		for n in range(math.ceil(len(boxes) / wrap)):

			row = boxes[n * wrap : (n + 1) * wrap]

			for line in range(len(row[0])):
				for box in row:
					beauty += box[line]
				beauty += "\n"

		return beauty.rstrip()
