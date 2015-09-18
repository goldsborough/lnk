#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""Data beautification."""

from __future__ import unicode_literals
from __future__ import division

import math
import os
import re
import sys

from collections import namedtuple

import lnk.errors

MAX_WIDTH = 60 # 3/4 of 80
# If we are connected to a terminal right now
if sys.stdin.isatty():
	with os.popen('stty size', 'r') as process:
		output = process.read()
	# Doesn't always work?
	if output:
		MAX_WIDTH = 3 * int(output.split()[1])//4

Line = namedtuple('Line', ['raw', 'escaped'])

def boxify(results):
	"""
	Formats results of command into a box.

	Arguments:
		results (list): A list of results, where each result is a list of lines
						(e.g. all the lines for the statistics of one URL).

	Returns:
		The results in a pretty box, as a string.
	"""
	if not results:
		raise lnk.errors.InternalError('Cannot boxify empty results!')
	results, width = get_escaped(results)
	border = '─' * (width + 2)
	lines = ['┌{0}┐'.format(border)]
	for n, result in enumerate(results):
		m = 0
		# We might add lines into the list mid-iteration
		while m < len(result):
			line = result[m]
			if len(line.escaped) > width:
				result = result[:m] + wrap(line, width) + result[m + 1:]
			else:
				adjusted = ljust(line, width)
				lines.append('│ {0} │'.format(adjusted))
				m += 1
		if n + 1 < len(results):
			lines.append('├{0}┤'.format(border))

	lines += ['└{0}┘'.format(border)]

	return '\n'.join(lines)

def wrap(line, width, indent=None):
	"""
	Wraps a line to a certain width.

	Why not textwrap.wrap? Because in this special situation it is necessary
	to wrap not only the escaped, plain-text string but *at the same time*
	also the raw string containing escape codes, which, however, should not
	count towards the length of a string. This method essentially wraps the
	plain-text string, while at the same time moving also through the raw
	string, but skipping escape-character-sequences when counting characters.

	Arguments:
		line (beauty.Line): The beauty.Line object to wrap.
		width (int): The width to which to wrap.
		indent (str): An indent string with which to indent all lines after the
					  first wrapped one.
	"""
	indent = indent or ' ' * int(math.ceil(width/10))
	escape_code = re.compile(r'\033\[(\d;?)+m')
	r_start = 0
	r = escape_code.match(line.raw)
	r = r.end() if r else 0
	e = 0
	e_start = 0
	wrapped = []
	while e <= len(line.escaped):
		w = width - len(indent) if len(wrapped) else width
		if (e > 0 and (e - e_start) == w) or (e == len(line.escaped)):
			stop = e_start - 1 if e_start else None
			reverse = line.escaped[e - 1:stop:-1]
			boundary = re.search(r'\w(?=\b)', reverse)
			index = e_start + (len(reverse) - boundary.end())
			# Only go backwards to the last word boundary if that
			# is not where we started (else just split it mid-word here).
			# If we went back to the start, we'd get an endless loop 
			if e < len(line.escaped) and index != e_start:
				# Go backwards to the last word boundary
				while e > index:
					match = re.match(r'm(;?\d)+\[\033', line.raw[e::-1])
					if match:
						r -= match.end()
					else:
						e -= 1
					r -= 1
			# If we already have one string wrapped
			if len(wrapped) > 0:
				raw = indent + line.raw[r_start:r]
				escaped = indent + line.escaped[e_start:e]
			else:
				raw = line.raw[r_start:r]
				escaped = line.escaped[e_start:e]
			wrapped.append(Line(raw, escaped))
			e_start = e
			r_start = r
		e += 1
		r += 1
		# Skip escape codes for the raw string
		match = escape_code.match(line.raw, r)
		if match:
			r = match.end()

	return wrapped

def ljust(line, width, padding=' '):
	"""
	Adds space-padding to the right of a line.

	ljust won't do because of the escaped/raw thing.

	Arguments:
		line (str): The line to adjust.
		width (int): The minimum width the string must have after this function.
		padding (str): Optionally, the string with which to pad (usually ' ').

	Returns:
		The adjusted raw line.
	"""
	return line.raw + padding * (width - len(line.escaped))

def get_escaped(results):
	"""
	Gets escaped lines for the results passed to boxify().

	Arguments:
		results (list): The results passed to boxify().

	Returns:
		A list of beauty.Line objects with a raw and escaped component.
	"""
	width = 0
	escaped = []
	for result in results:
		lines = []
		for line in result:
			line = escape(line)
			if len(line.escaped) > width:
				width = len(line.escaped)
			lines.append(line)
		escaped.append(lines)

	return escaped, min([MAX_WIDTH, width])

def escape(line):
	"""
	Escapes a raw string.

	Arguments:
		line (str): The raw string to escape.

	Returns:
		A beauty.Line object with the original raw component and the same
		string, but escaped, i.e. without the formatting codes applied by 
		ecstasy -- only the text.
	"""
	pattern = re.compile(r'^(.*)'    				# anything
						 r'(?:\033\[(?:\d;?)+m)'   	# escape codes
						 r'(.+)'				 	# formatted string
						 r'(?:\033\[(?:\d;?)+m)'   	# escape codes
						 r'(.*)$')					# anything
	line = line.rstrip()
	if '\033' in line:
		match = pattern.search(line)
		if not match:
			raise lnk.errors.InternalError("Could not parse '{0}'".format(line))
		escaped = ''.join([i for i in match.groups() if i])
	else:
		escaped = line

	return Line(line, escaped)
