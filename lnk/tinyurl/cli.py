#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

from service import Service

class Tinyurl(Service):

	@click.group()
	def run():
		pass

	@run.command()
	def link():
		pass

	@run.command()
	def stats():
		pass

	@run.command()
	def info():
		pass

	@run.command()
	def user():
		pass