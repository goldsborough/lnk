#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

@click.group()
def main():
	pass

@main.command()
def link():
	pass

@main.command()
def stats():
	pass

@main.command()
def info():
	pass

@main.command()
def user():
	pass