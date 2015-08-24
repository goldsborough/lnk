#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

from command import Command

def echo(*args):
	click.echo(User().fetch(*args))

class User(Command):
	def __init__(self, *args):
		pass

	def fetch(self):
		pass

	def get(self):
		pass