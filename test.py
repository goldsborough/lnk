#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import sys

def main():

	commands = [{
					"short": "v",
					"long": "verbose",
					"action": "?" # Found?
				},
				{
					"short": "u",
					"long": "use",
					"action": "+"    # Require argument
				}]

	if not args:
			# Display usage
			print("short url")
			pass

	n = 0

	while n < len(args):
		i = args[n]
		if i.startswith("-"):
			if i.startswith("--"):
				for command in commands:
					if i[2:] == command["long"]:
						if command["action"] == "?":
							command["found"] = True
						elif command["action"] == "+":
							if n == len(args) - 1:
								raise RuntimeError("Missing argument for '-" +
								                    command["short"] +
								                     "' option.")
							else:
								command["argument"] = args[n + 1]
								del args[n + 1]
						args.remove(i)
						n -= 1
						break
			else:
				for command in commands:
					if command["short"] in i[1:]:
						if command["action"] == "?":
							command["found"] = True
						elif command["action"] == "+":
							if i[::-1].find(command["short"]) or n == len(args) - 1:
								raise RuntimeError("Missing argument for '-" +
								                    command["short"] +
								                     "' option.")
							else:
								command["argument"] = args[n + 1]
								del args[n + 1]
						if len(i) == 2:
							del args[n]
							n -= 1
						else:
							args[n] = i = i.replace(command["short"], "")
		n += 1

	print(args)
	print(commands)

	"""
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

	
	responses = [ ]

	for unit in config["commands"]["stats"]["unit"]:
		parameters["unit"] = unit
		responses.append("│ {}:{} {}".format(unit.capitalize(),
			             " "*(len("minute") - len(unit)),
						 r("clicks", parameters)["link_clicks"]))

	length = len(max(responses, key=len)) + 1

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

