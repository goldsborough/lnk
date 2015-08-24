#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

from command import Command

def echo(*args):
	click.echo(User().fetch(*args))

class User(Command):
	def __init__(self):
		super(User, self).__init__('bitly', 'user')

	def fetch(self, *args):
		pass

	def get(self):
		pass