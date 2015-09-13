#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import apiclient.discovery
import click
import ecstasy
import httplib2
import oauth2client.file
import oauth2client.tools
import os.path
import warnings

from collections import namedtuple
from datetime import datetime, timedelta
from overrides import overrides

import beauty
import config
import errors

from googl.command import Command

warnings.filterwarnings('ignore', module=r'ecstasy\.parser')

def echo(*args):
	click.echo(History().fetch(*args))

class History(Command):

	Url = namedtuple('Url', ['short', 'long', 'created'])

	def __init__(self, raw=False):
		super(History, self).__init__('history')
		credentials_path = os.path.join(config.CONFIG_PATH, 'credentials')
		self.credentials = oauth2client.file.Storage(credentials_path)
		self.raw = raw
		self.delta = {
			"minute": timedelta(minutes=1), 
			"hour": timedelta(hours=1), 
			"day": timedelta(days=1),
			"week": timedelta(weeks=1), 
			"month": timedelta(weeks=4),
			"year": timedelta(weeks=52)
		}

	def fetch(self, last, ranges, forever, limit, expanded, both, pretty):
		data = self.request()
		urls = self.process(data)

		result = []
		if forever:
			result += self.forever(urls, limit, expanded, both, pretty)
		if ranges:
			result += self.ranges(urls, set(ranges), limit, expanded, both, pretty)
		if last:
			result += self.last(urls, set(last), limit, expanded, both, pretty)

		# Remove last empty line
		if pretty:
			del result[-1]

		if self.raw:
			return result
		return beauty.boxify([result]) if pretty else '\n'.join(result)

	def forever(self, urls, limit, expanded, both, pretty):
		lines = []
		for n, url in enumerate(urls):
			if n == limit:
				break
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return ['Since forever:'] + lines + [''] if pretty else lines

	def ranges(self, urls, ranges, limit, expanded, both, pretty):
		lines = []
		for timespan in ranges:
			if pretty:
				header = 'Between {0} {1}'.format(timespan[0], timespan[1])
				header += ' and {0} {1} ago:'.format(timespan[2], timespan[3])
				lines.append(header)
			begin = self.get_date(timespan[:2])
			end = self.get_date(timespan[2:])
			if end < begin:
				raise errors.UsageError("Illegal time range 'between {0} "
										"and {1} and {2} {3} ago' (start must"
										"precede end)"
										"!".format(timespan[0], timespan[1],
												   timespan[2], timespan[3]))
			filtered = self.filter(urls, begin, end)
			if filtered:
				lines += self.listify(filtered, limit, expanded, both, pretty)
			elif pretty:
				lines[-1] += ' None'

		return lines + [''] if pretty else lines

	def last(self, urls, last, limit, expanded, both, pretty):
		lines = []
		for timespan in last:
			if pretty:
				header = 'Last {0} {1}:'.format(timespan[0], timespan[1])
				lines.append(header)
			begin = self.get_date(timespan)
			filtered = self.filter(urls, begin, datetime.now())
			if filtered:
				lines += self.listify(filtered, limit, expanded, both, pretty)
			elif pretty:
				lines[-1] += ' None'

		return lines + [''] if pretty else lines

	def get_date(self, time_range):
		span = time_range[0]
		unit = time_range[1]
		if unit.endswith('s'):
			unit = unit[:-1]
		offset = span * self.delta[unit]

		return datetime.now() - offset

	def request(self):
		http = self.authorize()
		api = apiclient.discovery.build('urlshortener', 'v1', http=http)
		request = api.url().list()
		response = request.execute()
		self.verify(response, 'retrieve history')

		return response

	def authorize(self):
		credentials = self.credentials.get()
		if not credentials:
			logo = ecstasy.beautify('<lnk>', ecstasy.Style.Bold)
			details = 'You have not yet authorized {0} to '.format(logo)
			details += 'access your private goo.gl information. '
			details += "Please run 'lnk goo.gl key --generate'."
			raise errors.APIError('Missing authorization code!',
							      Details=details)
		http = httplib2.Http()
		if credentials.access_token_expired:
			credentials.refresh(http)
			self.credentials.put(credentials)
		credentials.authorize(http)

		return http

	def listify(self, urls, limit, expanded, both, pretty):
		lines = []
		for n, url in enumerate(urls):
			if n == limit:
				break
			line = self.lineify(url, expanded, both, pretty)
			lines.append(line)

		return lines

	@staticmethod
	@overrides
	def verify(response, what):
		if 'error' in response:
			raise errors.HTTPError('Could not {0}.'.format(what),
								   response['error']['code'],
						           response['error']['message'])

	@staticmethod
	def lineify(url, expanded, both, pretty):
		if both:
			line = '{0} => {1}'.format(url.short, url.long)
		elif expanded:
			line = url.long
		else:
			line = url.short

		if pretty:
			marked = ' <+> {0}'.format(line)
			line = ecstasy.beautify(marked, ecstasy.Color.Red)

		return line

	@staticmethod
	def filter(urls, begin, end):
		filtered = []
		for url in urls:
			if url.created >= begin and url.created <= end:
				filtered.append(url)

		return filtered

	@staticmethod
	def process(data):
		urls = []
		for item in data['items']:
			relevant = item['created'].split('.')[0]
			created = datetime.strptime(relevant, '%Y-%m-%dT%H:%M:%S')
			url = History.Url(item['id'], item['longUrl'], created)
			urls.append(url)

		return urls
