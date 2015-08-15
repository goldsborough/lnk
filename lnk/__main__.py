#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import ast
import click

import config

settings = config.get('settings')

available = "{0} or {1}".format(', '.join(settings['services'][:-1]),
								settings['services'][-1])

@click.command()
@click.option('-u', '--use',
			  type=(click.Choice(settings['services'])),
			  default=settings['default'],
			  metavar="SERVICE",
			  help="The URL shortening service to use ({})".format(available))
def shorten(use):
	#ast.literal_eval(use)
	print(use)

if __name__ == "__main__":
	shorten()
