#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config
import errors

import tinyurl.link

lnk_config = config.Manager('lnk')['settings']
tinyurl_config = config.Manager('tinyurl')
link_config = tinyurl_config['commands']['link']

@click.group(invoke_without_command=True,
			 no_args_is_help=True,
			 context_settings=dict(ignore_unknown_options=True))
@click.option('-v',
			  '--verbose',
			  count=True,
			  help='Controls the level of verbosity (in case of exceptions).')
@click.argument('args', nargs=-1)
@click.version_option(version=tinyurl_config['version'],
					  message='Bitly API v%(version)s')
@click.pass_context
def main(context, verbose, args):
	"""Tinyurl command-line client."""
	if verbose == 0:
		verbose = lnk_config['verbosity']
	if args[0] == 'link':
		args = args[1:] if args[1:] else ['--help']
	catch = errors.Catch(verbose, link.get_help(context))
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
	tinyurl.link.echo(copy, quiet, shorten + urls, pretty)
