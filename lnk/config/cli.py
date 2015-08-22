#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config

from service import Service


class Config(Service):

	@click.command()
	@click.argument('which', default='None')
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
				  default=False)
	@click.option('--all', '--all-keys', is_flag=True)
	def run(which, key, value, quiet, all_keys):
		if not key and not all_keys:
			Config.run(['--help'])
		elif which == 'None':
			Config.real_run('lnk', key, value, quiet, all_keys)
		else:
			Config.real_run(which, key, value, quiet, all_keys)

	@staticmethod
	def real_run(which, keys, values, quiet, all_keys):
		with config.Manager(which) as manager:
			keys = manager.keys if (not keys or all_keys) else list(keys)
			values = list(values)
			if quiet:
				while values:
					key = keys.pop(0)
					value = values.pop(0)
					manager[key] = int(value) if value.isdigit() else value
			else:
				lines = [Config.get_line(manager, key, values) for key in keys]
				click.echo("\n".join(lines))

	@staticmethod
	def get_line(manager, key, values):
		current = Config.get_value(manager[key])
		line = "{}: {}".format(key, ", ".join(current))
		if values:
			value = values.pop(0)
			manager[key] = int(value) if value.isdigit() else value
			line += " -> {}".format(manager[key])
		return line

	@staticmethod
	def get_value(value):
		if isinstance(value, list):
			return map(str, value)
		elif isinstance(value, dict):
			return ["{}: {}".format(k,v) for k,v in value.items()]
		return [str(value)]
