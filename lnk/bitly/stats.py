#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from command import Command

class Stats(Command):
	def __init__(self):

		super(Stats, self).__init__("stats")

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

		self.parameters["timezone"] = time.timezone // 3600

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

		self.info = []

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

		"""
		# Convert short ISO name (e.g. US)
		# to full name (e.g. United States)
		country = countries.get(alpha2=item["country"])
		"""

		return stats

	def retrieve(self, url, time, endpoints):

		stats = []

		self.parameters["link"] = url

		for endpoint in endpoints:

			result = {
				"type": endpoint,
				"times": []
			}

			for span, unit in time:

				timepoint = {
					"span" :  span,
					"unit": unit
				}

				# Get rid of the extra s in e.g. "weeks"
				self.parameters["unit"] = unit[:-1]

				self.parameters["units"] = span

				response = self.request(self.config["endpoints"][endpoint])

				self.verify(response, "retrieve {} for {}".format(endpoint, url))

				# clicks is the only one where the data
				# retrieved has a different name than its endpoint
				e = endpoint if endpoint != "clicks" else "link_clicks"

				timepoint["data"] = response["data"][e]

				result["times"].append(timepoint)

			stats.append(result)

		return stats
