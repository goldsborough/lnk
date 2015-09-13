#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re
import textwrap

from collections import namedtuple

with os.popen('stty size', 'r') as process:
	output = process.read()
MAX_WIDTH = 3 * int(output.split()[1])//4 if output else 80

def boxify(results):
	results, width = get_escaped(results)

	border = width + 2
	lines = ['┌{0}┐'.format('─' * border)]

	for n, result in enumerate(results):
		n = 0
		while n < len(result):
			line = result[n]
			if len(line.escaped) > width:
				wrapped = textwrap.wrap(line.raw,
										width=width,
										subsequent_indent=' ' * (width//10))
				escaped = [escape(i) for i in wrapped]
				result = result[:n] + escaped + result[n + 1:]
			else:
				adjusted = ljust(line, width)
				lines.append('│ {0} │'.format(adjusted))
				n += 1
		if n + 1 < len(results):
			lines.append('├{0}┤'.format('─' * border))

	lines += ['└{0}┘'.format('─' * border)]

	return '\n'.join(lines)

def ljust(line, width):
	return line.raw + ' ' * (width - len(line.escaped))

def get_escaped(results):
	width = 0
	mapped = []
	for result in results:
		lines = []
		for line in result:
			line = escape(line)
			if len(line.escaped) > width:
				width = len(line.escaped)
			lines.append(line)
		mapped.append(lines)

	if width > MAX_WIDTH:
		width = MAX_WIDTH

	return mapped, width

def escape(line):
	Line = namedtuple('Line', ['raw', 'escaped'])
	pattern = re.compile(r'^(.*)'    			# anything
					     r'(?:\033\[[\d;]+m)'   # escape codes
					     r'(.+)'			 	# formatted string
					     r'(?:\033\[[\d;]+m)'   # escape codes
					     r'(.*)$')				# anything

	if '\033' in line:
		match = pattern.search(line)
		escaped = ''.join([i for i in match.groups() if i])
	else:
		escaped = line

	return Line(line, escaped)
