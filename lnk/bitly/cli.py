#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import command
import config
import errors

import bitly.stats
import bitly.info
import bitly.link
import bitly.user
import bitly.history
import bitly.key

lnk_config = config.Manager('lnk')['settings']
bitly_config = config.Manager('bitly')

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
			 context_settings=dict(ignore_unknown_options=True))
@click.option('-v',
			  '--verbose',
			  count=True,
			  help='Controls the level of verbosity (in case of exceptions).')
@click.argument('args', nargs=-1)
@click.version_option(version=bitly_config['version'],
					  message='Bitly API v%(version)s')
@click.pass_context
def main(context, verbose, args):
	"""Bitly command-line client."""
	if verbose == 0:
		verbose = lnk_config['verbosity']
	name = args[0]
	if name not in bitly_config['commands'].keys():
		name = 'link'
	else:
		args = args[1:] if args[1:] else ['--help']
	which = globals()[name]
	catch = errors.Catch(verbose, which.get_help(context))
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
@click.argument('urls', nargs=-1)
def link(copy, quiet, expand, shorten, urls):
	"""Link shortening and expansion."""
	bitly.link.echo(copy, quiet, expand, shorten + urls)

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
	bitly.info.echo(only, hide, hide_empty, urls)

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
@click.option('-t',
			  '--time',
		      nargs=2,
		      multiple=True,
		      type=(int, click.Choice(units)),
		      help='Show statistics for this/these timespan(s).')
@click.option('--forever',
			  is_flag=True,
			  help='Show statistics for all timespans (since forever).')
@click.option('-l',
			  '--limit',
			  type=int,
			  default=stats_config['settings']['limit'],
			  help='Limit the amount of statistics retrieved per set.')
@click.option('-i',
			  '--info/--no-info',
			  default=stats_config['settings']['info'],
			  help='Also display information for each link.')
@click.option('-l/-s',
			  '--long/--short',
			  default=stats_config['settings']['long-countries'],
			  help='Whether to show long or short (abbreviated) country names.')
@click.argument('urls', nargs=-1)
def stats(only, hide, time, forever, limit, info, long, urls):
	"""Statistics and metrics for links."""
	bitly.stats.echo(only, hide, time, forever, limit, info, long, urls)

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
@click.option('-h',
			  '--history/--no-history',
			  default=user_config['settings']['history'],
			  help='Also show the user history (of links).')
@click.option('--hide-empty/--show-empty',
			  default=user_config['settings']['hide-empty'],
			  help='Whether to hide or show empty results.')
def user(only, hide, everything, history, hide_empty):
	"""Show meta-information for the current user."""
	bitly.user.echo(only, hide, everything, history, hide_empty)

@main.command()
@click.option('-t',
			  '--time',
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
			  help='Whether to show the history in a pretty box or as a raw list.')
def history(last, time_range, forever, limit, expanded, both, pretty):
	"""Retrieve link history."""
	if not last and not time_range and not forever:
		message = 'Please specify at least one time range (e.g. --forever)'
		raise click.UsageError(message)
	# Default case for both
	if not both and expanded is None:
		both = True
	bitly.history.echo(last, time_range, forever, limit, expanded, both, pretty)

@main.command()
@click.option('--generate',
			  is_flag=True,
			  help='Generate a new api key (asks for login/password).')
@click.option('-l',
			  '--login',
			  prompt=True,
			  help='Generate a new api key with this login.')
@click.option('-p',
			  '--password',
			  prompt=True,
			  hide_input=True,
              confirmation_prompt=True,
              help='Generate a new api key with this password.')
@click.option('-s/-h',
			  '--show/--hide',
			  default=key_config['settings']['show'],
			  help='Whether to show or hide the generated API key.')
def key(generate, login, password, show):
	"""Generate an API key for user metrics and history."""
	bitly.key.echo(generate, login, password, show)
