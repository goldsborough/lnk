#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""The command-line interface to the config command."""

import click

import config.manager
import config.configure
import errors

allowed_wich = config.manager.get('lnk', 'services') + ['lnk']

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
			  metavar='KEY')
@click.option('-v',
			  '--value',
			  nargs=1,
			  multiple=True,
			  metavar='VALUE')
@click.option('-q/-l',
			  '--quiet/--loud',
			  default=False)
@click.option('-a',
			  '--all',
			  '--all-keys',
			  is_flag=True)
def main(which, command, key, value, quiet, all_keys):
	"""Configuration interface."""
	if command:
		if which == 'lnk':
			what = 'lnk has no commands to configure.'
			hint = "If '{0}' is a key, you ".format(command)
			hint += "probably wanted to use '-k {0}'.".format(command)
			raise errors.UsageError(what, Hint=hint)
		elif command not in config.get(which, 'commands').keys():
			what = "No such command '{0}' for {1}.".format(command, which)
			raise errors.UsageError(what)
	if key or all_keys:
		errors.catch(config.configure.echo,
					 which,
					 command,
					 key,
					 value,
					 quiet,
					 all_keys)
	else:
		main(['--help'])
