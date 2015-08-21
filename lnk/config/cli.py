#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

from service import Service
from config.manager import Manager

class Config(Service):

	@click.command()
	@click.option('-k',
				  '--key',
				  nargs=1,
				  multiple=True,
				  metavar='KEY')
	@click.option('-v',
				  '--value',
				  nargs=1,
				  multiple=True,
				  metavar='VALUE')
	@click.option('-q/-l',
				  '--quiet/--loud',
				  default=False) # for quiet
	@click.argument('which', default='lnk')
	def run(key, value, quiet, which):
		with Manager(which) as config:
			keys = list(key) if key else config.keys
			values = list(value)
			if quiet:
				while values:
					key = keys.pop(0)
					value = values.pop(0)
					config[key] = int(value) if value.isdigit() else value
			else:
				lines = [Config.get_line(config, key, values) for key in keys]
				click.echo("\n".join(lines))

	@staticmethod
	def get_line(config, key, values):
		current = Config.get_value(config[key])
		line = "{}: {}".format(key, ", ".join(current))
		if values:
			value = values.pop(0)
			config[key] = int(value) if value.isdigit() else value
			line += " -> {}".format(config[key])
		return line

	@staticmethod
	def get_value(value):
		if isinstance(value, list):
			return map(str, value)
		elif isinstance(value, dict):
			return ["{}: {}".format(k,v) for k,v in value.items()]
		return [str(value)]
