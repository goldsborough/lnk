#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click
import os
import sys

import bitly.info
#import link
#import stats

sys.path.insert(0, os.path.abspath('..'))

#from pycountry import countries

@click.group()
def bitly():
	print("Bitly")

@bitly.command()
def link():
	print("Link")

@bitly.command()
def info():
	print("Info")

@bitly.command()
def stats():
	print("Stats")

@bitly.command()
def user():
	print("User")