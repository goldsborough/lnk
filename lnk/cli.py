#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import os

import config

class Main(click.MultiCommand):

	def list_commands(self, context):
		commands = ['config']
		for service in config.Manager('lnk')['services']:
			commands.append(service.replace('.', ''))
		return commands
			
	def get_command(self, context, name):
		namespace = {}
		directory = os.path.dirname(__file__)
		filename = os.path.join(directory, name, 'cli.py')
		with open(filename) as source:
			code = compile(source.read(), filename, 'exec')
			eval(code, namespace, namespace)
		return getattr(namespace[name.title()], 'run')

main = Main()