#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os

def beautify(boxes):

	return Beautifier().beautify(boxes)

class Box:
	def __init__(self, parent=None, children=[]):

		self.parent = parent

		self.children = children

class Beautifier:
	def __init__(self):

		self.vertical = chr(0x2502)
		self.horizontal = chr(0x2500)

		self.leftBottom = chr(0x2514)
		self.rightBottom = chr(0x2518)

		self.leftTop = chr(0x250c)
		self.rightTop = chr(0x2510)

		self.leftMiddle = chr(0x251c)
		self.rightMiddle =  chr(0x2524)

	def beautify(self, boxes):

		if type(boxes) != list:
			boxes = [boxes]

		self.widths = self.getWidths(boxes)

		lines = self.unify(boxes)

		return (self.vertical + "\n").join(lines)

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

			# "not n" makes 0 (first position) evaluate to True
			first = not n and not depth

			last = n + 1 == len(boxes) and "sub" not in box

			lines.extend(self.boxify(box, self.widths[depth], last, first))

			if "sub" in box:
				subs = []
				# Gather lines from all sub units
				# and unify them into a single unit
				for pos, sub in enumerate(box["sub"]):

					subUnits = self.unify(sub, depth + 1)

					for line, unit in enumerate(subUnits):
						# If this is the first line found at this
						# position rjust it by the width of boxes
						# at this depth mulitiplied by the number of
						# (sub) boxes that are supposed to be next to it
						if line == len(subs):
							subs.append(unit.rjust(pos * self.widths[depth]))
						else:
							subs[line] += unit

				# Add right border now
				lines.extend(subs)

		return lines

	def boxify(self, box, width, last=False, first=False):

		data = box["data"]

		lines = [ ]

		# + 2 for left and right space
		middle = self.horizontal * (width + 2)

		if first:
			lines.append("{}{}{}".format(self.leftTop,
										 middle,
										 self.rightTop))

		if type(data) == str:
			string = data.upper() if first else data.title()
			lines.append("{} {} ".format(self.vertical, 
								          self.center(string, width)))

			if last:
				lines.append(self.leftBottom + middle + self.rightBottom)

		else: # dict
			keyWidth = len(max(data, key=len))

			for key, value in data.items():

				string = (key + ":").ljust(keyWidth + 2).title() + str(value)


				lines.append("{} {} ".format(self.vertical,
											 string.ljust(width)))

			left = self.leftBottom if last else self.leftMiddle

			right = self.rightBottom if last else self.rightMiddle

			lines.append("{}{}{}".format(left, middle, right))

		return lines

	def center(self, string, width):
		length = len(string)

		left = length + (width - length)//2

		return string.rjust(left).ljust(width)