#!/usr/local/bin/python3

import sys
import json

import bitly

from errors import Error

class Short:
	def __init__(self, args):

		if not args:
			# Display usage
			print("short [-e] url")

		with open("config.json") as file:
			self.config = json.loads(file.read())

		(verbose, service), args = self.parse(args)

		try:

			print(getattr(eval(service), "handle")(args))

		except Error as e:
			print(e.verbose if verbose else e.what)


	def parse(self, args):

		options = [{	
						"short": "v",
						"long": "verbose",
						"action": "?", 		# True/False
						"result": False
					},
					{
						"short": "u",
						"long": "use",
						"action": "!",    	# Require
						"choices": list(self.config.keys())[1:],
						"result": self.config["default"]
					}]

		n = 0

		while n < len(args):
			i = args[n]
			if i.startswith("-"):
				if i.startswith("--"):
					for option in options:
						if i[2:] == option["long"]:
							if option["action"] == "?":
								option["result"] = True
							elif option["action"] == "!":
								if n == len(args) - 1:
									raise Error("Missing argument for '-" +
												 option["short"] +
										         "' option.")
								else:
									option["result"] = args[n + 1]
									del args[n + 1]
							args.remove(i)
							n -= 1
							break
				else:
					for option in options:
						if option["short"] in i[1:]:
							if option["action"] == "?":
								option["result"] = True
							elif option["action"] == "!":
								if i[::-1].find(option["short"]) or n == len(args) - 1:
									raise Error("Missing argument for '-" +
												 option["short"] + "' option.")
								elif args[n + 1] not in option["choices"]:
									raise Error("Invalid service '" +
									            args[n + 1] + "'.")
								else:
									option["result"] = args[n + 1]
									del args[n + 1]
							if len(i) == 2:
								del args[n]
								n -= 1
								break
							else:
								args[n] = i = i.replace(option["short"], "")
			n += 1

		return (i["result"] for i in options), args


if __name__ == "__main__":

	Short(sys.argv[1:])
