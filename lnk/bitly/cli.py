#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

import config

from bitly.info import Info
from bitly.link import Link
from bitly.stats import Stats
from bitly.user import User

from service import Service

#from pycountry import countries

manager = config.Manager('bitly')

info = manager['commands']['info']
stats = manager['commands']['stats']

class Bitly(Service):

	@click.group()
	@click.option('-v', '--verbose', count=True)
	def run(verbose):
		if verbose == 0:
			with config.Manager('lnk') as lnk:
				verbose = lnk['verbosity']

	@run.command()
	@click.option('-e', '--expand', is_flag=True)
	@click.argument('urls', nargs=-1)
	def link():
		print("Link")

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
		Info(only, hide, urls)

	@run.command()
	@click.argument('urls', nargs=-1)
	def stats(urls):
		Stats(urls)

	@run.command()
	@click.argument('urls', nargs=-1)
	def user():
		print("User")