#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""The command-line interface to the bit.ly client."""

import click

import lnk.cli
import lnk.config
import lnk.errors

import lnk.bitly.stats
import lnk.bitly.info
import lnk.bitly.link
import lnk.bitly.user
import lnk.bitly.history
import lnk.bitly.key

lnk_config = lnk.config.Manager('lnk')['settings']
bitly_config = lnk.config.Manager('bitly')

link_config = bitly_config['commands']['link']
info_config = bitly_config['commands']['info']
stats_config = bitly_config['commands']['stats']
user_config = bitly_config['commands']['user']
history_config = bitly_config['commands']['history']
key_config = bitly_config['commands']['key']

units = stats_config['units']
units += ['{0}s'.format(i) for i in units]

display = history_config['settings']['display']
expanded_default = None if display == 'both' else display == 'expanded'

@click.group(invoke_without_command=True,
			 no_args_is_help=True,
			 context_settings=dict(ignore_unknown_options=True),
			 help='bit.ly command-line client.')
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
@click.version_option(version=bitly_config['version'],
					  message='bit.ly API v%(version)s')
@click.pass_context
def main(context, verbose, level, args):
	"""
	Main entry-point to the bit.ly API from the command-line.

	All command-calls are handled here. Before passing on all command-specific
	arguments to the appropriate command, the verbosity setting is handled here,
	which is of use when catching any exceptions thrown by any commands.
	Moreover, this entry-point takes care of making the 'link' command of the
	service its default command, such that the user can type 'lnk ...' when
	meaning 'lnk bitly link ...'.
	"""
	verbosity = lnk.cli.get_verbosity(verbose, level)
	# Could be the name of the command, or the first argument if the command
	# was not specified (meaning the link command is requested)
	if not args or args[0] not in bitly_config['commands'].keys():
		name = name = bitly_config['settings']['command']
	else:
		name = args[0]
		args = args[1:] or ['--help']
	# Pick out the function (command)
	which = globals()[name]
	catch = lnk.errors.Catch(verbosity, which.get_help(context), 'bitly')
	catch.catch(which.main, args, standalone_mode=False)

@main.command()
@click.option('-c/-n',
			  '--copy/--no-copy',
			  default=lnk_config['copy'],
			  help='Whether or not to copy the first link to the clipboard.')
@click.option('-q/-l',
			  '--quiet/--loud',
			  default=False,
			  help='Whether or not to print warnings.')
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
	if not urls and not expand and not shorten:
		raise lnk.errors.UsageError('Please supply at least one URL.')
	lnk.bitly.link.echo(copy, quiet, expand, shorten + urls, pretty)

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
@click.option('--hide-empty/--show-empty',
			  default=info_config['settings']['hide-empty'],
			  help='Whether to hide or show empty results.')
@click.argument('urls', nargs=-1)
def info(only, hide, hide_empty, urls):
	"""Information about links."""
	# Its' horrible to handle the missing parameter when click
	# throws an exception (doesn't make it accessible), so just do it here.
	if not urls:
		raise lnk.errors.UsageError('Please supply at least one URL.')
	lnk.bitly.info.echo(only, hide, hide_empty, urls)

@main.command()
@click.option('-o',
   			  '--only',
   		 	  multiple=True,
   			  type=click.Choice(stats_config['sets']),
   			  help='Display only this/these set(s) of statistics.')
@click.option('-h',
			  '--hide',
			  multiple=True,
   			  type=click.Choice(stats_config['sets']),
   			  help='Hide this/these set(s) of statistics.')
@click.option('-l',
			  '--last',
		      nargs=2,
		      multiple=True,
		      type=(int, click.Choice(units)),
		      help='Show statistics for this/these timespan(s).')
@click.option('--forever',
			  is_flag=True,
			  help='Show statistics for all timespans (since forever).')
@click.option('--limit',
			  type=int,
			  default=stats_config['settings']['limit'],
			  help='Limit the amount of statistics per timespan.')
@click.option('-a',
			  '--all',
			  '--no-limit',
			  is_flag=True,
			  help='Have no limit on the amount of statistics per timespan.')
@click.option('-i',
			  '--info/--no-info',
			  default=stats_config['settings']['info'],
			  help='Also display information for each link.')
@click.option('-f/-s',
			  '--full/--short',
			  default=stats_config['settings']['full-countries'],
			  help='Whether to show full or short (abbreviated) country names.')
@click.argument('urls', nargs=-1)
def stats(only, hide, last, forever, limit, no_limit, info, full, urls):
	"""Statistics and metrics for links."""
	if not urls:
		raise lnk.errors.UsageError('Please supply at least one URL.')
	limit = None if no_limit else limit
	lnk.bitly.stats.echo(only, hide, last, forever, limit, info, full, urls)

@main.command()
@click.option('-o',
   			  '--only',
   		 	  multiple=True,
   			  type=click.Choice(user_config['sets']),
   			  help='Display only this/these set(s) of user information.')
@click.option('-h',
			  '--hide',
			  multiple=True,
   			  type=click.Choice(user_config['sets']),
   			  help='Hide this/these set(s) of user information.')
@click.option('-e/-a',
			  '--everything/--all',
			  is_flag=True,
			  help='Display all sets of user information.')
@click.option('--history/--no-history',
			  default=user_config['settings']['history'],
			  help='Also show the user history (of links).')
@click.option('--hide-empty/--show-empty',
			  default=user_config['settings']['hide-empty'],
			  help='Whether to hide or show empty results.')
def user(only, hide, everything, history, hide_empty):
	"""Show meta-information for the current user."""
	lnk.bitly.user.echo(only, hide, everything, history, hide_empty)

@main.command()
@click.option('-l',
		      '--last',
		      nargs=2,
		      multiple=True,
		      type=(int, click.Choice(units)),
		      help='Display history of links from this time range, relative to now.')
@click.option('-r',
			  '--range',
		      '--time-range',
		      nargs=4,
		      multiple=True,
		      type=(int, click.Choice(units), int, click.Choice(units)),
		      help='Display history of links from this time range.')
@click.option('--forever',
			  is_flag=True,
			  help='Display history of links since forever.')
@click.option('-l',
			  '--limit',
			  type=int,
			  default=history_config['settings']['limit'],
			  help='Limit the number of links shown per time range.')
@click.option('-a',
			  '--all',
			  '--no-limit',
			  is_flag=True,
			  help='Have no limit on the number of links per timespan.')
@click.option('-e/-s',
			  '--expanded/--short',
			  default=expanded_default,
			  help='Whether to show expanded or shortened links.')
@click.option('-b',
			  '--both',
			  is_flag=True,
			  help='Whether to show expanded and shortened links.')
@click.option('--pretty/--plain',
			  default=history_config['settings']['pretty'],
			  help='Whether to show the history in a pretty box or as a plain list.')
def history(last, time_range, forever, limit, no_limit, expanded, both, pretty):
	"""Retrieve link history."""
	if not last and not time_range:
		forever = True
	# Default case for both
	if not both and expanded is None:
		both = True
	limit = None if no_limit else limit
	lnk.bitly.history.echo(last, time_range, forever, limit, expanded, both, pretty)

@main.command()
@click.option('-g',
			  '--generate',
			  is_flag=True,
			  help='Generate a new api key (asks for login/password).')
@click.option('-l',
			  '--login',
			  help='Generate a new api key with this login.')
@click.option('-p',
			  '--password',
              help='Generate a new api key with this password.')
@click.option('-s/-h',
			  '--show/--hide',
			  default=key_config['settings']['show'],
			  help='Whether to show or hide the generated API key.')
@click.option('-w',
			  '--who',
			  is_flag=True,
			  help='Show who is currently logged in.')
def key(generate, login, password, show, who):
	"""Authorization management."""
	lnk.bitly.key.echo(generate, login, password, show, who)
