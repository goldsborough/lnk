#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config

import bitly.info
import bitly.link
import bitly.stats
import bitly.user

from service import Service

manager = config.Manager('bitly')

info = manager['commands']['info']
stats = manager['commands']['stats']
stats = manager['commands']['user']

class Bitly(Service):

	@click.group(invoke_without_command=True,
				 no_args_is_help=True,
				 context_settings=dict(ignore_unknown_options=True))
	@click.option('-v', '--verbose', count=True)
	@click.argument('args', nargs=-1)
	@click.version_option(version=manager['version'],
						  message='Bitly API v%(version)s')
	@click.pass_context
	def run(context, verbose, args):
		if verbose == 0:
			with config.Manager('lnk') as lnk:
				verbose = lnk['verbosity']
		if args[0] in ['stats', 'info', 'user', 'link']:
			getattr(Bitly, args[0])(args[1:])
		else:
			Bitly.link(args)
			

	@run.command()
	@click.option('-e',
				  '--expand',
				  multiple=True)
	@click.option('-s',
				  '--shorten',
				  multiple=True)
	@click.argument('urls', nargs=-1)
	def link(expand, shorten, urls):
		bitly.link.handle(expand, shorten + urls)

	@run.command()
	@click.option('-o',
				  '--only',
				  nargs=1,
				  multiple=True,
				  type=(click.Choice(info['sets'])))
	@click.option('-h',
				  '--hide',
				  nargs=1,
				  multiple=True,
				  type=(click.Choice(info['sets'])))
	@click.argument('urls', nargs=-1)
	def info(only, hide, urls):
		bitly.info.handle(only, hide, urls)

	@run.command()
	@click.option('--long/--short', default=True)
	@click.argument('urls', nargs=-1)
	def stats(urls, long):
		bitly.stats.Stats(urls)

	@run.command()
	def user():
		bitly.user.User()
