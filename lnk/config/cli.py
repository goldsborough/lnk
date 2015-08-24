#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config
import errors

from service import Service


class Config(Service):

	@click.command()
	@click.argument('which', default='lnk')
	@click.argument('command', default='None')
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
	def run(which, command, key, value, quiet, all_keys):
		if key or all_keys:
			errors.catch(0,
						 Config.real_run,
						 which, command,
						 key,
						 value,
						 quiet,
						 all_keys)
		else:
			Config.run(['--help'])

	@staticmethod
	def real_run(which, command, keys, values, quiet, all_keys):
		with config.Manager(which, write=True) as manager:
			if command != 'None':
				manager = manager['commands'][command]
			manager = manager['settings']
			keys = manager.keys() if (not keys or all_keys) else list(keys)
			values = list(values)
			if quiet:
				while values:
					key = keys.pop(0)
					Config.assert_key_is_valid(key, manager)
					value = values.pop(0)
					manager[key] = int(value) if value.isdigit() else value

			else:
				lines = [Config.get_line(manager, key, values) for key in keys]
				click.echo("\n".join(lines))

	@staticmethod
	def get_line(manager, key, values):
		Config.assert_key_is_valid(key, manager)
		current = Config.get_value(manager[key])
		line = "{}: {}".format(key, ", ".join(current))
		if values:
			value = values.pop(0)
			manager[key] = int(value) if value.isdigit() else value
			line += " => {}".format(manager[key])
		return line

	@staticmethod
	def get_value(value):
		if isinstance(value, list):
			return map(str, value)
		elif isinstance(value, dict):
			return ["{}: {}".format(k,v) for k,v in value.items()]
		return [str(value)]

	@staticmethod
	def assert_key_is_valid(key, manager):
		if key not in manager:
			raise errors.InvalidKeyError("Key '{0}' not found.".format(key))
