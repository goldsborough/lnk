#!/usr/local/bin/python3

import sys
import json
import argparse

import bitly
import errors

def short(args):

	with open("config.json") as file:
		config = json.loads(file.read())

	parser = argparse.ArgumentParser(prog="short",
								     description="Command-line URL\
								 		      	  shortening tool")

	parser.add_argument("-v",
						"--verbose",
					    action="store_true")
	
	parser.add_argument("-u",
						"--use",
						choices=config["services"].keys(),
						default=config["default"])

	parser.add_argument("args", nargs='*')

	args = vars(parser.parse_args(args))

	verbose = args.pop("verbose")

	try:
		print(getattr(eval(args.pop("use")), "handle")(args["args"]))

	except errors.Error as e:
		print(e.verbose if verbose else e.what)

	except Exception as e:
		raise e#print(e.message)

if __name__ == "__main__":

	short(sys.argv[1:])