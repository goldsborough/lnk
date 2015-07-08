#!/usr/local/bin/python3

import argparse
import json

if __name__ == "__main__":

	config = {}

	with open("config.json") as file:
		config = json.loads(file.read())["services"]["bitly"]

	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers()

	link = subparsers.add_parser("link")

	link.set_defaults(handler=self.link)

	link.add_argument("-e",
					  "--expand",
					  action="store_true")

	link.add_argument("url")

	stats = subparsers.add_parser("stats", aliases=["statistics"])

	stats.set_defaults(handler=self.stats)

	stats.add_argument("-o",
					   "--only",
					   choices=config["stats"]["sets"])

	stats.add_argument("-u",
					   "--unit",
					   choices=config["stats"]["units"])

	stats.add_argument("-r",
					   "--restrict",
					   type=int)

	stats.add_argument("url")

	args = "stats -o clicks -u day -r 3 http://bitly.com/2l3kh"

	print(parser.parse_args(args.split()))