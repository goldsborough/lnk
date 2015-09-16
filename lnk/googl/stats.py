#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import ecstasy

import abstract
import beauty
import countries

from googl.command import Command

def echo(*args):
	click.echo(Stats().fetch(*args))

class Stats(Command):

	def __init__(self, raw=False):
		super(Stats, self).__init__('stats')
		self.raw = raw

	def fetch(self, only, hide, times, forever, limit, add_info, full, urls):
		sets = abstract.filter_sets(self.sets, only, hide)
		timespans = self.get_timespans(times, forever)

		results = []
		threads = []
		for url in urls:
			self.queue.put(url)
			args = (results, sets, timespans, add_info, full, limit)
			thread = self.new_thread(self.get_stats, *args)
			threads.append(thread)
		self.join(threads)

		return results if self.raw else beauty.boxify(results)

	def get_stats(self, results, sets, timespans, add_info, full, limit):
		data = self.request(add_info)
		lines = self.lineify(data, sets, timespans, full, limit)
		with self.lock:
			results.append(lines)

	def request(self, add_info):
		url = self.queue.get()
		what = "get information for '{0}'".format(url)
		response = self.get(url, 'FULL', what)

		response['URL'] = url
		del response['kind']
		del response['id']
		if not add_info:
			for i in ['created', 'longUrl', 'status']:
				del response[i]

		return response

	def lineify(self, data, sets, timespans, full, limit): 
		stats = data.pop('analytics')
		statistics = self.listify(stats, sets, timespans, full, limit)
		header = [self.format(key, value) for key, value in data.items()]

		return header + statistics

	def listify(self, data, sets, timespans, full, limit):
		lines = []
		for display, real in sets.items():
			lines.append('{0}:'.format(display.title()))
			for timespan, categories in data.items():
				# Ignore unwanted timespans
				if timespan not in timespans:
					continue
				lines.append(self.get_header(timespan))
				# The goo.gl API does not include categories with zero
				# clicks thus we first have to determine whether the
				# category is present at all
				if not categories.get(real):
					lines[-1] += ' None'
				elif display == 'clicks':
					lines[-1] += ' {0}'.format(categories[real])
				else:
					lines += self.sub_listify(display,
											  categories[real],
											  limit,
											  full)
		return lines

	def get_header(self, timespan):
		if timespan == 'allTime':
			header = 'Since forever:'
		else:
			if timespan == 'twoHours':
				timespan = 'two hours'
			header = 'Last {0}:'.format(timespan)

		return self.list_item.format(header)

	def sub_listify(self, category, points, limit, full):
		lines = []
		for n, point in enumerate(points):
			if n == limit:
				break
			subject = point['id']
			if subject == 'unknown':
				subject = subject.title()
			if category == 'countries' and full:
				subject = countries.names[subject]
			clicks = point['count']
			line = ecstasy.beautify('   <-> {0}: {1}', ecstasy.Color.Yellow)
			lines.append(line.format(subject, clicks))

		return lines

	def get_timespans(self, times, forever):
		timespans = set(times)
		if not timespans and not forever:
			default = self.settings['timespan']
			if default == 'forever':
				timespans.add('allTime')
			elif default == 'two-hours':
				timespans.add('twoHours')
			else:
				timespans.add(default)
		if forever:
			timespans.add('allTime')
		if 'two-hours' in timespans:
			timespans.remove('two-hours')
			timespans.add('twoHours')

		return timespans

	@staticmethod
	def format(key, value):
		if key == 'shortUrlClicks':
			key = 'clicks'
		elif key == 'longUrl':
			key = 'expanded'
		key = '<{0}>: {1}'.format(key.title(), value)

		return ecstasy.beautify(key, ecstasy.Color.Red)
