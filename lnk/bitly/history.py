#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

from command import Command

def echo(*args):
	click.echo(History().fetch(*args))

class History(Command):
	def __init__(self, raw=False):
		#super(History, self).__init__('bitly', 'history')
		self.raw = raw

	def fetch(self):
		pass
