#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config
import errors

import bitly.info
import bitly.link
import bitly.stats
import bitly.user

from service import Service

settings = config.Manager('lnk')
service = config.Manager('bitly')

info = service['commands']['info']
stats = service['commands']['stats']
stats = service['commands']['user']

class Bitly(Service):

	@click.group(invoke_without_command=True,
				 no_args_is_help=True,
				 context_settings=dict(ignore_unknown_options=True))
	@click.option('-v',
				  '--verbose',
				  count=True,
				  default=settings['verbosity'])
	@click.argument('args', nargs=-1)
	@click.version_option(version=service['version'],
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
				  default=settings['copy'])
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
				  type=click.Choice(info['sets']))
	@click.option('-h',
				  '--hide',
				  nargs=1,
				  multiple=True,
				  type=click.Choice(info['sets']))
	@click.argument('urls', nargs=-1)
	def info(only, hide, urls):
		bitly.info.echo(only, hide, urls)

	@run.command()
	@click.option('--long/--short', default=True)
	@click.argument('urls', nargs=-1)
	def stats(urls, long):
		bitly.stats.Stats(urls)

	@run.command()
	def user():
		bitly.user.User()
