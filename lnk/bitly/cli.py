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

from service import Service

lnk_config = config.Manager('lnk')
bitly_config = config.Manager('bitly')

info_config = bitly_config['commands']['info']
stats_config = bitly_config['commands']['stats']
user_config = bitly_config['commands']['user']

units = stats_config['units']
units += ['{0}s'.format(i) for i in units]

class Bitly(Service):

	@click.group(invoke_without_command=True,
				 no_args_is_help=True,
				 context_settings=dict(ignore_unknown_options=True))
	@click.option('-v',
				  '--verbose',
				  count=True,
				  default=lnk_config['verbosity'])
	@click.argument('args', nargs=-1)
	@click.version_option(version=bitly_config['version'],
						  message='Bitly API v%(version)s')
	@click.pass_context
	def run(context, verbose, args):
		if verbose == 0:
			with config.Manager('lnk') as lnk:
				verbose = lnk['verbosity']
		if args[0] in ['stats', 'info', 'user', 'link']:
			command = args[0]
			args = args[1:] if args[1:] else ['--help']
			errors.catch(verbose, getattr(Bitly, command), args)
		else:
			errors.catch(verbose, Bitly.link, args)
			

	@run.command()
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

	@run.command()
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
	@click.argument('urls', nargs=-1)
	def info(only, hide, urls):
		bitly.info.echo(only, hide, urls)

	@run.command()
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
				  default=stats_config['defaults']['limit'])
	@click.option('-i',
				  '--info/--no-info',
				  default=stats_config['defaults']['info'])
	@click.option('-f/-s',
				  '--full-countries/--short-countries',
				  default=stats_config['defaults']['full-countries'])
	@click.argument('urls', nargs=-1)
	def stats(only, hide, time, forever, limit, info, full_countries, urls):
		bitly.stats.echo(only, hide, time, forever, limit, info, full_countries, urls)

	@run.command()
	def user():
		bitly.user.User()
