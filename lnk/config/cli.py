#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""The command-line interface to the config command."""

import click

import config.configure
import errors

@click.command()
@click.argument('service', default='lnk')
@click.argument('command', default=None, required=False)
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
def main(service, command, key, value, quiet, all_keys):
	"""Configuration interface."""
	if key or all_keys:
		errors.catch(config.configure.configure,
					 service,
					 command,
					 key,
					 value,
					 quiet,
					 all_keys)
	else:
		main(['--help'])
