#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import click

@click.command()
def shorten():
	click.echo("Hello")

if __name__ == "__main__":
	shorten()
