#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Handles the oauth2 authorization procedure for the goo.gl API."""

import click
import ecstasy
import oauth2client.file
import oauth2client.tools
import os.path
import webbrowser

from oauth2client.client import OAuth2WebServerFlow

import lnk.errors
import lnk.config

from lnk.googl.command import Command

CLIENT_ID = '324510822959-qcp2d36tkl07v2dfqde3ungmpii4qv96.apps.googleusercontent.com'
CLIENT_SECRET = 'r7-N-xmGbfePxZP3q6QEXu1Z'
SCOPE = 'https://www.googleapis.com/auth/urlshortener'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def echo(*args):
	"""
	Executes a key command.

	Arguments:
		args (variadic): The arguments to pass to a
						 Key instance's fetch() method.
	"""
	Key().fetch(*args)

class Key(Command):
	"""
	Handles oauth2 authorization for the goo.gl API.

	The authorization procedure involves exchaning a temporary authorization
	code for an oauth2 token. When executing this command, the user will be
	redirected to a web-page where he or she can authorize lnk to access his
	or her private goo.gl information. Once done the user gets an
	authorization-code which he or she must then paste into the command-line,
	where it is fetched by lnk and stored for authorization during HTTP requests.

	Attributes:
		raw (bool): Whether or not to return the raw output for internal use
					or the prettified output for outside representation.
		flow (oauth2client.client.OAuth2WebServerFlow): An object from Google's
										API-library that is used for the entire
										authorization-code-to-oauth2-token
										exchange procedure.
		credentials_path (str): The path to the credentials file in the config
								folder.
	"""
	def __init__(self, raw=False):
		super(Key, self).__init__('key')
		self.raw = raw
		self.flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
										client_secret=CLIENT_SECRET,
										scope=SCOPE,
										redirect_uri=REDIRECT_URI)
		self.credentials_path = os.path.join(lnk.config.CONFIG_PATH, '.credentials')


	def fetch(self, _):

		# First request an authorization token as part of the oauth handshake.
		authorize_url = self.flow.step1_get_authorize_url()

		# The user is redirected to Google's authorization page where permission
		# must be granted to the lnk application to access the user's data
		click.echo("Redirecting you to Google's authorization page ...")
		webbrowser.open(authorize_url)

		code = click.prompt('Please enter the authorization code',
							hide_input=True)

		# Now exchange the authorization token for credentials, i.e.
		# an access_token that must be passed as part of the oauth protocol
		# with any API call, and a refresh_token that can be used to refresh
		# the access_token, which expires after a certain time (~ 1 hour).
		credentials = self.flow.step2_exchange(code)

		storage = oauth2client.file.Storage(self.credentials_path)
		storage.put(credentials)

		success = ecstasy.beautify('<Success!>', ecstasy.Color.Magenta)
		click.echo(success)
