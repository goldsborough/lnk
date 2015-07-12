#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import sys

def main():

	config = { }

	with open("config.json") as file:
		config = json.loads(file.read())["bitly"]

	parameters = {
				  	"link": "http://bit.ly/1M8RyFd",
				   	"access_token": config["key"],
				   	"units": 1
				 }

	r = lambda e, p: requests.get(config["api"] +
						       "v{}/".format(config["version"]) +
		                       config["commands"]["stats"]["endpoints"][e],
		                       params=p).json()["data"]

	config = config["commands"]["stats"]

	parser = argparse.ArgumentParser()

	parser.add_argument("-o",
				   		"--only",
				   		action="append",
				   		choices=config["sets"])

	parser.add_argument("-a",
					    "--all",
					    action="store_true")

	parser.add_argument("-t",
					    "--time",
					    action="append",
					    nargs=2)

	parser.add_argument("url")

	args = parser.parse_args("-o clicks -t 4 week bitly.com".split())

	print(args)

	"""
	responses = [ ]

	for unit in config["commands"]["stats"]["unit"]:
		parameters["unit"] = unit
		responses.append("│ {}:{} {}".format(unit.capitalize(),
			             " "*(len("minute") - len(unit)),
						 r("clicks", parameters)["link_clicks"]))

	length = len(max(responses, key=len)) + 1
	"""
	"""
	s = "┌" + "─" * (length - 3) + "┐\n"

	s += "│  " + "CLICKS" + "   │\n"

	s += "├" + "─" * (length - 3) + "┤\n"

	for i in responses:
		s += i.ljust(length) + "│\n"

	s += "└" + "─" * (length - 3) + "┘"

	print(s)
	"""

if __name__ == "__main__":

	main()

