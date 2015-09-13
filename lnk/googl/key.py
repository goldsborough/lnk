#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import oauth2client.file
import oauth2client.tools
import os.path
import webbrowser

from oauth2client.client import OAuth2WebServerFlow

import errors
import config

from googl.command import Command

CLIENT_ID = '324510822959-qcp2d36tkl07v2dfqde3ungmpii4qv96.apps.googleusercontent.com'
CLIENT_SECRET = 'r7-N-xmGbfePxZP3q6QEXu1Z'
SCOPE = 'https://www.googleapis.com/auth/urlshortener'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def echo(*args):
	click.echo(Key().fetch(*args), nl=False)

class Key(Command):

	def __init__(self, raw=False):
		super(Key, self).__init__('key')
		self.raw = raw
		self.flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
										client_secret=CLIENT_SECRET,
										scope=SCOPE,
										redirect_uri=REDIRECT_URI)
		self.destination = os.path.join(config.CONFIG_PATH, 'credentials')


	def fetch(self, _):

		# First request an authorization token as part of the oauth handshake.
		authorize_url = self.flow.step1_get_authorize_url()

		# The user is redirected to Google's authorization page where permission
		# must be granted to the lnk application to access the user's data
		click.echo("Redirecting you to Google's authorization page ...")
		webbrowser.open(authorize_url)

		code = click.prompt('Please enter the authorization code')

		# Now exchange the authorization token for credentials, i.e.
		# an access_token that must be passed as part of the oauth protocol
		# with any API call, and a refresh_token that can be used to refresh
		# the access_token, which expires after a certain time (~ 1 hour).
		credentials = self.flow.step2_exchange(code)

		storage = oauth2client.file.Storage(self.destination)
		storage.put(credentials)

		return ''
