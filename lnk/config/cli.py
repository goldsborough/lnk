#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import os
import json

@click.group()
@click.option('-k', '--key', nargs=1, multiple=True, metavar='KEY')
@click.option('-v', '--value', nargs=1, multiple=True, metavar='VALUE')
def config(context, ):
	pass