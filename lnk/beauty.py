#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division

import math
import os
import re
import sys

from collections import namedtuple

import errors

MAX_WIDTH = 60
if sys.stdin.isatty():
	with os.popen('stty size', 'r') as process:
		output = process.read()
	if output:
		MAX_WIDTH = 3 * int(output.split()[1])//4

Line = namedtuple('Line', ['raw', 'escaped'])

def boxify(results):
	if not results:
		raise errors.InternalError('Cannot boxify empty results!')

	results, width = get_escaped(results)

	border = '─' * (width + 2)
	lines = ['┌{0}┐'.format(border)]

	for n, result in enumerate(results):
		m = 0
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
			if e < len(line.escaped) and index != e_start:
				while e > index:
					match = re.match(r'm(;?\d)+\[\033', line.raw[e::-1])
					if match:
						r -= match.end()
					else:
						e -= 1
					r -= 1
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
		match = escape_code.match(line.raw, r)
		if match:
			r = match.end()

	return wrapped

def ljust(line, width):
	return line.raw + ' ' * (width - len(line.escaped))

def get_escaped(results):
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
	pattern = re.compile(r'^(.*)'    				# anything
						 r'(?:\033\[(?:\d;?)+m)'   	# escape codes
						 r'(.+)'				 	# formatted string
						 r'(?:\033\[(?:\d;?)+m)'   	# escape codes
						 r'(.*)$')					# anything

	if '\033' in line:
		match = pattern.search(line)
		if not match:
			raise errors.InternalError("Could not parse '{0}'".format(line))
		escaped = ''.join([i for i in match.groups() if i])
	else:
		escaped = line

	return Line(line, escaped)
