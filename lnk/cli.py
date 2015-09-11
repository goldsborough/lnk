#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import os

import config

class Main(click.MultiCommand):

	def __init__(self):
		super(Main, self).__init__(context_settings=dict(
								  ignore_unknown_options=True))
		self.commands = {}
		with config.Manager('lnk') as manager:
			self.default = manager['settings']['service']
			for command in manager['services'] + ['config']:
				command = command.replace('.', '') # goo.gl -> googl
				self.commands[command] = self.get_function(command)

	def invoke(self, context):
		escaped = context.args[0].replace('.', '')
		if escaped not in self.commands.keys():
			context.args.insert(0, self.default)
		else:
			context.args[0] = escaped
		super(Main, self).invoke(context)

	def list_commands(self, context):
		return self.commands.keys()
			
	def get_command(self, context, name):
		return self.commands[name]

	@staticmethod
	def get_function(name):
		namespace = {}
		directory = os.path.dirname(__file__)
		filename = os.path.join(directory, name, 'cli.py')
		with open(filename) as source:
			code = compile(source.read(), filename, 'exec')
			eval(code, namespace, namespace)
		return namespace['main']

def main(args):
	command = Main()
	command.main(args, standalone_mode=False)
