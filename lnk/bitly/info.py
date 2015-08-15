#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from command import Command

class Info(Command):
	def __init__(self):

		super(Info, self).__init__("info")

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

	def parse(self, args):

		args = self.parser.parse_args(args)

		sets = args.only if args.only else self.config["sets"].keys()

		if args.hide:
			for i in args.hide:
				sets.remove(i)

		sets = [self.config["sets"][key] for key in sets]

		info = []

		for url in args.urls:

			result = self.retrieve(url, sets)

			mapped = {}

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

		return info

	def retrieve(self, url, sets):

		self.parameters["shortUrl"] = url

		response = self.request(self.config["endpoints"]["info"])

		self.check(response,
				   "retrieve information for " + url,
				   "info")

		response = response["data"]["info"][0]

		return {i : response[i] for i in response if i in sets}
