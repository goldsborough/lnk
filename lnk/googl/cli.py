#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config
import errors

import googl.link
import googl.info
import googl.stats
import googl.history
import googl.user
import googl.key

lnk_config = config.Manager('lnk')['settings']
googl_config = config.Manager('googl')

link_config = googl_config['commands']['link']
info_config = googl_config['commands']['info']
stats_config = googl_config['commands']['stats']
user_config = googl_config['commands']['user']
history_config = googl_config['commands']['history']
key_config = googl_config['commands']['key']

units = stats_config['units']
units += ['{0}s'.format(i) for i in units]

display = history_config['settings']['display']
expanded_default = None if display == 'both' else display == 'expanded'

@click.group(invoke_without_command=True,
			 no_args_is_help=True,
			 context_settings=dict(ignore_unknown_options=True))
@click.option('-v',
			  '--verbose',
			  count=True,
			  help='Controls the level of verbosity (in case of exceptions).')
@click.argument('args', nargs=-1)
@click.version_option(version=googl_config['version'],
					  message='goo.gl API v%(version)s')
@click.pass_context
def main(context, verbose, args):
	"""goo.gl command-line client."""
	if verbose == 0:
		verbose = lnk_config['verbosity']
	name = args[0]
	if name not in googl_config['commands'].keys():
		name = 'link'
	else:
		args = args[1:] if args[1:] else ['--help']
	which = globals()[name]
	catch = errors.Catch(verbose, which.get_help(context), 'goo.gl')
	catch.catch(which.main, args, standalone_mode=False)

@main.command()
@click.option('-c/-n',
			  '--copy/--no-copy',
			  default=lnk_config['copy'],
			  help='Whether or not to copy the first link to the clipboard.')
@click.option('-q/-l',
			  '--quiet/--loud',
			  default=False,
			  help='Whether or not to print the expanded/shortened links.')
@click.option('-e',
			  '--expand',
			  multiple=True,
			  metavar='URL',
			  help='Expand a short url (bitlink).')
@click.option('-s',
			  '--shorten',
			  multiple=True,
			  metavar='URL',
			  help='Shorten a long url.')
@click.option('--pretty/--plain',
			  default=link_config['settings']['pretty'],
			  help='Whether to show the links in a pretty box or as a plain list.')
@click.argument('urls', nargs=-1)
def link(copy, quiet, expand, shorten, urls, pretty):
	"""Link shortening and expansion."""
	googl.link.echo(copy, quiet, expand, shorten + urls, pretty)

@main.command()
@click.option('-o',
			  '--only',
			  nargs=1,
			  multiple=True,
			  type=click.Choice(info_config['sets']),
			  help='Display only this/these set(s) of information.')
@click.option('-h',
			  '--hide',
			  nargs=1,
			  multiple=True,
			  type=click.Choice(info_config['sets']),
			  help='Hide this/these set(s) of information.')
@click.argument('urls', nargs=-1)
def info(only, hide, urls):
	"""Information about links."""
	googl.info.echo(only, hide, urls)