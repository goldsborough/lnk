#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import ecstasy

import countries

from googl.command import Command

def echo(*args):
	click.echo(Stats().fetch(*args))

class Stats(Command):

	def __init__(self, raw=False):
		super(Stats, self).__init__('stats')

		self.raw = raw
		self.parameters['projection'] = 'FULL'

	def fetch(self, only, hide, times, forever, limit, add_info, full, urls):
		sets = self.filter(only, hide)
		timespans = self.get_timespans(times, forever)

		results = []
		threads = []
		for url in urls:
			self.queue.put(url)
			thread = self.new_thread(self.request,
									 results,
									 sets,
									 timespans,
									 add_info,
									 full,
									 limit)
			threads.append(thread)
		self.join(threads)

		return results if self.raw else self.boxify(results)

	def request(self, results, sets, timespans, add_info, full, limit):
		url = self.queue.get()
		response = self.get(self.endpoints['stats'], dict(shortUrl=url))
		what = "retrieve information for '{0}'".format(url)
		data = self.verify(response, what)

		del data['kind']
		del data['id']
		if not add_info:
			for i in ['created', 'longUrl', 'status']:
				del data[i]

		data['URL'] = url
		lines = self.lineify(data, sets, timespans, full, limit)

		self.lock.acquire()
		results.append(lines)
		self.lock.release()

	def filter(self, only, hide):
		sets = self.sets
		if only:
			sets = {k:v for k,v in sets.items() if k in only}
		for i in hide:
			del sets[i]

		return sets

	def lineify(self, data, sets, timespans, full, limit): 
		anal = data.pop('analytics')
		statistics = self.listify(anal, sets, timespans, full, limit)
		header = [self.format(key, value) for key, value in data.items()]

		return header + statistics

	def listify(self, data, sets, timespans, full, limit):
		lines = []
		for display, real in sets.items():
			lines.append('{0}:'.format(display.title()))
			for timespan, categories in data.items():

				# ignore unwanted timespans
				if timespan not in timespans:
					continue
				elif timespan == 'allTime':
					lines.append(' + Since forever:')
				else:
					lines.append(' + Last {0}:'.format(timespan))

				# The goo.gl API does not include categories with zero
				# clicks thus we first have to determine whether the
				# category is present at all
				if real in categories:
					if display == 'clicks':
						lines[-1] += ' {0}'.format(categories[real])
					else:
						lines += self.sub_listify(display,
												  categories[real],
												  limit,
												  full)
				else:
					lines[-1] += ' None'

		return lines

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
			lines.append('   - {0}: {1}'.format(subject, clicks))

		return lines

	def get_timespans(self, times, forever):
		timespans = set(times)
		if not timespans and not forever:
			default = self.settings['unit']
			timespans.add(default if default != 'forever' else 'allTime')
		if forever:
			timespans.add('allTime')

		return timespans

	@staticmethod
	def format(key, value):
		if key == 'shortUrlClicks':
			key = 'clicks'
		elif key == 'longUrl':
			key = 'expanded'
		key = '<{0}>: {1}'.format(key.title(), value)

		return ecstasy.beautify(key, ecstasy.Color.Red)
