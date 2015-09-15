#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import ecstasy
import time

from collections import namedtuple

import beauty
import countries
import bitly.info

from bitly.command import Command, filter_sets

def echo(*args):
	click.echo(Stats().fetch(*args))

class Stats(Command):

	Timespan = namedtuple('Timespan', ['span', 'unit'])

	def __init__(self, raw=False):
		super(Stats, self).__init__('stats')

		self.raw = raw
		self.info = bitly.info.Info(raw=True)
		self.parameters['timezone'] = time.timezone // 3600

	def fetch(self, only, hide, times, forever, limit, add_info, full, urls):
		self.parameters['limit'] = limit

		sets = filter_sets(self.sets, only, hide)
		timespans = self.get_timespans(times, forever)
		info = self.info.fetch(only, hide, False, urls) if add_info else []

		results = []
		for n, url in enumerate(urls):
			header = info[n] if add_info else ['URL: {0}'.format(url)]
			data = self.request_all(url, timespans, sets)
			lines = self.lineify(data, full)

			results.append(header + lines)

		return results if self.raw else beauty.boxify(results)

	def request_all(self, url, timespans, sets):
		parameters = {'link': url}
		result = {}
		threads = []
		for endpoint in sets:
			result[endpoint] = []
			for timespan in timespans:

				parameters['unit'] = timespan.unit

				if timespan.unit.endswith('s'):
					# Get rid of the plural s in e.g. 'weeks'
					parameters['unit'] = timespan.unit[:-1]

				parameters['units'] = timespan.span

				self.queue.put((url, endpoint, timespan, parameters))
				threads.append(self.new_thread(self.request, result))
		self.join(threads)

		return result

	def request(self, results):
		url, endpoint, timespan, parameters = self.queue.get()

		response = self.get(self.endpoints[endpoint], parameters)
		what = "retrieve {0} for '{1}'".format(endpoint, url)
		response = self.verify(response, what)

		# For 'clicks' the key has a different name than the endpoint
		e = endpoint if endpoint != 'clicks' else 'link_clicks'

		data = {'timespan': timespan, 'data': response[e]}

		self.lock.acquire()
		results[endpoint].append(data)
		self.lock.release()

	def get_timespans(self, times, forever):
		timespans = set()
		if not times:
			unit = self.settings['unit']
			span = self.settings['span']
			if unit == 'forever':
				timespans.add(Stats.Timespan(-1, 'day'))
			elif 'year' in unit:
				timespans.add(Stats.Timespan(span * 12, 'months'))
			else:
				timespans.add(Stats.Timespan(span, unit))
		else:
			if forever:
				# -1 = since forever (unit could be any)
				timespans.add(Stats.Timespan(-1, 'day'))
			for span, unit in times:
				if 'year' in unit:
					span *= 12
					unit = 'months'
				timespans.add(Stats.Timespan(span, unit))

		return timespans

	def lineify(self, data, full): 
		lines = []
		for subject, items in data.items():
			lines.append('{0}:'.format(subject.title()))
			lines += self.listify(subject, items, full)

		return lines

	def listify(self, subject, data, full):
		lines = []
		for result in data:
			timespan = result['timespan']
			items = result['data']

			if timespan.span == -1:
				line = 'Since forever'
			else:
				line = 'Last {0} {1}'.format(timespan.span, timespan.unit)

			line = '{0}:'.format(self.list_item.format(line))
			lines.append(line)

			if not items:
				lines[-1] += ' None'
				continue

			if isinstance(items, list):
				for item in items:
					clicks = item.pop('clicks')
					key = item.values()[0]
					line = self.format(subject, key, clicks, full)
					lines.append(line)
			else:
				# for clicks
				lines[-1] += ' {0}'.format(items)

		return lines

	@staticmethod
	def format(subject, key, value, full):
		if subject == 'countries':
			if key == 'None':
				key = 'Other'
		 	elif full:
				key = countries.names[key]
		elif key == 'direct':
			key = key.title()
		line = '   <-> {0}: {1}'.format(key, value)
		pretty = ecstasy.beautify(line, ecstasy.Color.Yellow)

		return pretty
