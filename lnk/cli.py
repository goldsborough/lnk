#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import json
import os

folder = os.path.dirname(__file__)

class Main(click.MultiCommand):

	def list_commands(self, context):
		config = os.path.join(folder, "config", "config.json")
		commands = ['config']
		with open(config) as config:
			for cmd in json.loads(config.read())['services']:
				commands.append(cmd.replace('.', ''))
		return commands
			
	def get_command(self, context, name):
		namespace = {}
		filename = os.path.join(folder, name, "cli.py")
		with open(filename) as file:
			code = compile(file.read(), filename, 'exec')
			eval(code, namespace, namespace)
		return namespace[name]

main = Main()