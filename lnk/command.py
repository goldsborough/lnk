#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import json
import re
import requests

import errors

class Command(object):
	def __init__(self, command):

		with open("../config/config.json") as file:
			config = json.loads(file.read())["bitly"]

		self.api = config["api"] + "v{}".format(config["version"])

		self.config = config["commands"][command]

		self.parameters = {"access_token": config["key"]}

		self.http = re.compile(r"http(s?)://")

	def parse(self):
		raise NotImplementedError

	def request(self, endpoint):

		response = requests.get("{}/{}".format(self.api, endpoint),
							    params=self.parameters)

		return response.json()

	@staticmethod
	def verify(response, what, sub=None):

		if not str(response["status_code"]).startswith('2'):
			raise errors.HTTPError("Could not {}.".format(what),
						    response["status_code"],
				            response["status_txt"])

		data = response["data"][sub][0] if sub else response["data"]

		if "error" in data:
			raise errors.APIError("Could not {}.".format(what),
			                	  data["error"])
