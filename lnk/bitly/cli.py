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

lnk_config = config.Manager('lnk')['settings']
bitly_config = config.Manager('bitly')

info_config = bitly_config['commands']['info']
stats_config = bitly_config['commands']['stats']
user_config = bitly_config['commands']['user']
history_config = bitly_config['commands']['history']

units = stats_config['units']
units += ['{0}s'.format(i) for i in units]

display = history_config['settings']['display']
expanded_default = None if display == 'both' else display == 'expanded'

@click.group(invoke_without_command=True,
			 no_args_is_help=True,
			 context_settings=dict(ignore_unknown_options=True))
@click.option('-v',
			  '--verbose',
			  count=True)
@click.argument('args', nargs=-1)
@click.version_option(version=bitly_config['version'],
					  message='Bitly API v%(version)s')
@click.pass_context
def main(context, verbose, args):
	if verbose == 0:
		verbose = lnk_config['verbosity']
	name = args[0]
	if name not in bitly_config['commands'].keys():
		name = 'link'
	else:
		args = args[1:] if args[1:] else ['--help']
	catch = errors.Catch(verbose)
	catch.catch(globals()[name].main, args, standalone_mode=False)

@main.command()
@click.option('-c/-n',
			  '--copy/--no-copy',
			  default=lnk_config['copy'])
@click.option('-q/-l',
			  '--quiet/--loud',
			  default=False)
@click.option('-e',
			  '--expand',
			  multiple=True)
@click.option('-s',
			  '--shorten',
			  multiple=True)
@click.argument('urls', nargs=-1)
def link(copy, quiet, expand, shorten, urls):
	bitly.link.echo(copy, quiet, expand, shorten + urls)

@main.command()
@click.option('-o',
			  '--only',
			  nargs=1,
			  multiple=True,
			  type=click.Choice(info_config['sets']))
@click.option('-h',
			  '--hide',
			  nargs=1,
			  multiple=True,
			  type=click.Choice(info_config['sets']))
@click.option('--hide-empty',
				  is_flag=True)
@click.argument('urls', nargs=-1)
def info(only, hide, hide_empty, urls):
	bitly.info.echo(only, hide, hide_empty, urls)

@main.command()
@click.option('-o',
   			  '--only',
   		 	  multiple=True,
   			  type=click.Choice(stats_config['sets']))
@click.option('-h',
				  '--hide',
			  multiple=True,
   			  type=click.Choice(stats_config['sets']))
@click.option('-t',
			      '--time',
		      nargs=2,
		      multiple=True,
		      type=(int, click.Choice(units)))
@click.option('--forever',
			  is_flag=True)
@click.option('-l',
			  '--limit',
			  type=int,
			  default=stats_config['settings']['limit'])
@click.option('-i',
			  '--info/--no-info',
			  default=stats_config['settings']['info'])
@click.option('-l/-s',
			  '--long/--short',
			  default=stats_config['settings']['long-countries'])
@click.argument('urls', nargs=-1)
def stats(only, hide, time, forever, limit, info, long, urls):
	bitly.stats.echo(only, hide, time, forever, limit, info, long, urls)

@main.command()
@click.option('-o',
   			  '--only',
   		 	  multiple=True,
   			  type=click.Choice(user_config['sets']))
@click.option('-h',
				  '--hide',
			  multiple=True,
   			  type=click.Choice(user_config['sets']))
@click.option('-e/-a',
				  '--everything/--all',
				  is_flag=True)
@click.option('-h',
				  '--history/--no-history',
				  default=user_config['settings']['history'])
@click.option('--hide-empty',
				  is_flag=True)
def user(only, hide, everything, history, hide_empty):
	bitly.user.echo(only, hide, everything, history, hide_empty)

@main.command()
@click.option('-t',
			  '--time',
			      '--last',
		      nargs=2,
		      multiple=True,
		      type=(int, click.Choice(units)))
@click.option('-r',
			  '--range',
			      '--time-range',
		      nargs=4,
		      multiple=True,
		      type=(int, click.Choice(units), int, click.Choice(units)))
@click.option('--forever',
			  is_flag=True)
@click.option('-l',
			  '--limit',
			  type=int,
			  default=history_config['settings']['limit'])
@click.option('-e/-s',
			  '--expanded/--short',
			  default=expanded_default)
@click.option('-b',
			  '--both',
			  is_flag=True)
@click.option('--list',
			  '--listed',
			  is_flag=True)
def history(last, time_range, forever, limit, expanded, both, listed):
	if not last and not time_range and not forever:
		message = 'Please specify at least one time range (e.g. --forever)'
		raise click.UsageError(message)
	bitly.history.echo(set(last), set(time_range), forever, limit, expanded, both, listed)
