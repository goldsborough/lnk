#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""The command-line interface to the config command."""

import click

import lnk.config.manager
import lnk.config.configure
import lnk.errors

allowed_wich = lnk.config.manager.get('lnk', 'services') + ['lnk', 'config']

@click.command()
@click.argument('which',
				default='lnk',
				type=click.Choice(allowed_wich))
@click.argument('command',
				default=None,
				required=False)
@click.option('-k',
			  '--key',
			  nargs=1,
			  multiple=True,
			  metavar='KEY',
			  help='A key to show or manipulate.')
@click.option('-v',
			  '--value',
			  nargs=1,
			  multiple=True,
			  metavar='VALUE',
			  help='A new value for a key.')
@click.option('-q/-l',
			  '--quiet/--loud',
			  default=False,
			  help='Whether to visualize changes.')
@click.option('-a',
			  '--all',
			  '--all-keys',
			  is_flag=True,
			  help='Whether to show all keys.')
def main(which, command, key, value, quiet, all_keys):
	"""Configuration interface."""
	if command:
		if which == 'lnk':
			what = 'lnk has no commands to configure.'
			hint = "If '{0}' is a key, you ".format(command)
			hint += "probably wanted to use '-k {0}'.".format(command)
			raise lnk.errors.UsageError(what, Hint=hint)
		elif command not in lnk.config.get(which, 'commands').keys():
			what = "No such command '{0}' for {1}.".format(command, which)
			raise lnk.errors.UsageError(what)
	if key or all_keys:
		lnk.errors.catch(lnk.config.configure.echo,
						 which,
						 command,
						 key,
						 value,
						 quiet,
						 all_keys)
	else:
		main(['--help'])
