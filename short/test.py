#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import sys

class Beautifier:
	def __init__(self):

		pass

	def beautify(self, boxes):

		print(boxes)

		widths = self.getWidths(boxes)

		units = self.unify(boxes, widths)

		self.vertical = chr(0x2502),
		self.horizontal = chr(0x2500),

		self.leftBottom = chr(0x2514),
		self.rightBottom = chr(0x2518),

		self.leftTop = chr(0x250c),
		self.rightTop = chr(0x2510),

		self.leftMiddle = chr(0x251c),
		self.rightMiddle =  chr(0x2524)

	def getWidths(self, boxes, depth = 1):

		widths = [ 0 ]

		for box in boxes:

			if "sub" in box:
				subs = []
				for sub in box["sub"]:
					subs.append(self.getWidths(sub))

				# Go to the maximum depth
				for n in range(len(max(subs, key=len))):
					width = 0
					# Find the maximum width between
					# all subs at this depth
					for i in subs:
						if n < len(i) and i[n] > width:
							width = i[n]

					# Not appended yet at this depth
					if len(widths) == depth + n:
						widths.append(width)
					else:
						widths[depth + n] = width

				# Get the total width of the maximum width mulitplied
				# by the number of subs and see if it is greater than
				# the current maximum width
				sub = widths[1] * len(box["sub"])

				if sub > widths[0]:
					widths[0] = sub

			if type(box["data"]) == str:
				width = len(box["data"])

			else:
				width = self.getDictionaryWidth(box["data"])

			if width > widths[0]:
				widths[0] = width

		return widths

	def getDictionaryWidth(self, dictionary):

		keys = len(max(map(str, dictionary.keys()), key=len))

		values = len(max(map(str, dictionary.values()), key=len))

		# + 2 for the ": " in "key: value"
		return keys + values + 2

	def unify(self, boxes, depth = 0):

		lines = [ ]

		for n, box in enumerate(boxes):

			last = False

			if "sub" in box:
				subs = []
				# Gather lines from all sub units
				# and unify them into a single unit
				for pos, sub in enumerate(box["sub"]):
					subUnits = self.beautify(sub, depth + 1)
					for line, unit in enumerate(subUnits):
						# If this is the first line found at this
						# position rjust it by the width of boxes
						# at this depth mulitiplied by the number of
						# (sub) boxes that are supposed to be next to it
						if line == len(subs):
							subs.append(unit.rjust(pos * self.widths[depth]))
						else:
							subs[line] += unit
				lines.extend(subs)

			elif n + 1 == len(boxes):
				last = True

			# not n makes 0 (first position) evaluate to True
			box = self.boxify(box, self.widths[depth], last, not n)

			lines.extend()

		return lines

	def concatenate(self, units):

		# Add units together
		# Add bottom border
		# Add right border
		# Fuck bitches

	def boxify(self, box, width, last=False, first=False):

		data = box["data"]

		lines = [ ]

		# + 2 for left and right space
		middle = self.horizontal * width + 2

		if first:
			beauty += "{}{}{}\n".format(self.leftTop,
								      middle,
								      self.rightTop)

		if type(data) == str:
			beauty += "{0} {1} {0}\n".format(self.vertical,
										     self.center(data, width))

		else: # dict
			keyWidth = len(max(data, key=len))

			for key, value in data.items():

				item = "{} {}".format((key + ":").ljust(keyWidth), value)
				
				beauty += "{0} {1} {0}".format(self.vertical,
											   self.center(item, width))

		left = self.leftBottom if last else self.leftMiddle

		right = self.rightBottom if laset else self.rightMiddle

		beauty += "{}{}{}".format(left, middle, right)

		return beauty

	def center(self, string, width):
		length = len(string)

		left = length + (width - length)//2

		return string.rjust(left).ljust(width)


def main():

	print(Beautifer().beautify)

if __name__ == "__main__":

	main()

