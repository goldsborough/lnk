#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Entry point for the CLI."""

import sys
import cli

args = sys.argv

# If stdin is not empty (being piped to)
if not sys.stdin.isatty():
	args += sys.stdin.readlines()

cli.main(args[1:])
