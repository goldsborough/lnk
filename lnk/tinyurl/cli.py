#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""The command-line interface to the bit.ly client."""

import click

import lnk.cli
import lnk.config
import lnk.errors

import lnk.tinyurl.link

lnk_config = lnk.config.Manager('lnk')['settings']
tinyurl_config = lnk.config.Manager('tinyurl')
link_config = tinyurl_config['commands']['link']

@click.group(invoke_without_command=True,
			 no_args_is_help=True,
			 context_settings=dict(ignore_unknown_options=True),
			 help='tinyurl command-line client.')
@click.option('-v',
			  '--verbose',
			  count=True,
			  help='Increments the level of verbosity.')
@click.option('-l',
			  '--level',
			  nargs=1,
			  type=int,
			  help='Controls the level of verbosity.')
@click.argument('args', nargs=-1)
@click.version_option(version=tinyurl_config['version'],
					  message='tinyurl API v%(version)s')
@click.pass_context
def main(context, verbose, level, args):
	"""
	Main entry-point to the tinyurl API from the command-line.

	All command-calls are handled here. Before passing on all command-specific
	arguments to the appropriate command, the verbosity setting is handled here,
	which is of use when catching any exceptions thrown by any commands.
	Moreover, this entry-point takes care of making the 'link' command of the
	service its default command, such that the user can type 'lnk ...' when
	meaning 'lnk tinyurl link ...'.
	"""
	verbosity = lnk.cli.get_verbosity(verbose, level)
	if args and args[0] == tinyurl_config['settings']['command']:
		args = args[1:] or ['--help']
	catch = lnk.errors.Catch(verbosity, link.get_help(context))
	catch.catch(link.main, args, standalone_mode=False)

@main.command()
@click.option('-c/-n',
			  '--copy/--no-copy',
			  default=lnk_config['copy'],
			  help='Whether or not to copy the first link to the clipboard.')
@click.option('-q/-l',
			  '--quiet/--loud',
			  default=False,
			  help='Whether or not to print the shortened links.')
@click.option('-s',
			  '--shorten',
			  multiple=True,
			  metavar='URL',
			  help='Shorten a long url.')
@click.option('--pretty/--plain',
			  default=link_config['settings']['pretty'],
			  help='Whether to show the links in a pretty box or as a plain list.')
@click.argument('urls', nargs=-1)
def link(copy, quiet, shorten, urls, pretty):
	"""Link shortening."""
	if not urls and not shorten:
		raise lnk.errors.UsageError('Please supply at least one URL.')
	lnk.tinyurl.link.echo(copy, quiet, shorten + urls, pretty)
