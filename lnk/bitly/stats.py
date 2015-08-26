#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import ecstasy
import time
import threading

from collections import namedtuple

import bitly.countries
import bitly.info

from command import Command

def echo(*args):
	click.echo(Stats().fetch(*args))

class Stats(Command):

	Timespan = namedtuple('Timespan', ['span', 'unit'])

	def __init__(self, raw=False):
		super(Stats, self).__init__('bitly', 'stats')

		self.raw = raw
		self.info = bitly.info.Info(raw=True)
		self.parameters['timezone'] = time.timezone // 3600

	def fetch(self, only, hide, times, forever, limit, add_info, full, urls):
		self.parameters['limit'] = limit

		sets = self.filter(only, hide)

		timespans = self.get_timespans(times, forever)

		info = self.info.fetch(only, hide, urls) if add_info else []

		result = []
		for n, url in enumerate(urls):
			header = info[n] if add_info else ['URL: {0}'.format(url)]

			for n, line in enumerate(header):
				colon = line.find(':')
				line = '<{0}>{1}'.format(line[:colon], line[colon:])
				line = ecstasy.beautify(line, ecstasy.Color.Red)
				header[n] = line

			data = self.request(url, timespans, sets)
			lines = self.lineify(data, full)

			result.append(header + lines)

		return result if self.raw else self.boxify(result)

	def request(self, url, timespans, sets):
		parameters = {'link': url}
		results = {}
		for endpoint in sets:
			results[endpoint] = []
			for timespan in timespans:

				parameters['unit'] = timespan.unit

				if timespan.unit.endswith('s'):
					# Get rid of the plural s in e.g. 'weeks'
					parameters['unit'] = timespan.unit[:-1]

				parameters['units'] = timespan.span

				self.queue.put((url, endpoint, timespan, parameters))
				self.new_thread(self.retrieve, results)

		self.queue.join()

		return results

	def retrieve(self, results):
		url, endpoint, timespan, parameters = self.queue.get()

		response = self.request(self.endpoints[endpoint], parameters)
		what = 'retrieve {0} for {1}'.format(endpoint, url)
		response = self.verify(response, what)

		# For 'clicks' the key has a different name than the endpoint
		e = endpoint if endpoint != 'clicks' else 'link_clicks'

		data = {'timespan': timespan, 'data': response['data'][e]}

		self.lock.acquire()
		results[endpoint].append(data)
		self.lock.release()

		self.queue.task_done()

	def filter(self, only, hide):
		sets = self.sets
		if only:
			sets = [i for i in sets if i in only]
		for i in hide:
			del sets[i]
		return sets

	def get_timespans(self, times, forever):
		timespans = set()
		if not times:
			unit = self.settings['unit']
			if unit == 'forever':
				timespans.add(Stats.Timespan(-1, 'day'))
			else:
				timespans.add(Stats.Timespan(self.settings['span'], unit))
		else:
			if forever:
				# -1 = since forever (unit could be any)
				timespans.add(Stats.Timespan(-1, 'day'))
			for span, unit in times:
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

			lines.append(' + {0}:'.format(line))

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
				key = bitly.countries.names[key]
		elif key == 'direct':
			key = key.title()

		return '  - {0}: {1}'.format(key, value)
