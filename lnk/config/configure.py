#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Methods used to configure settings in the config files.

Note that these methods are not in any-way object-oriented or
general-purpose, they solely execute the config command.
"""

import click

import lnk.config


def echo(*args):
	"""
	Echoes the return value of configure() to stdout.

	Arguments:
		args (variadic): The arguments to forward to configure().
	"""
	click.echo(configure(*args), nl=False)


def configure(which, command, keys, values, quiet, all_keys):
	"""
	Does the actual configuration-management.

	Arguments:
		which (str): The configuration file for which to configure settings
					 (e.g. 'lnk' or 'bitly').
		command (str): Optionally, the command of the which for which
					   to configure settings (e.g. 'link').
		keys (tuple): The keys to show.
		values (tuple): The values to give the keys.
		quiet (bool): Whether to output anything or just do the
					 configuration quietly.
		all_keys (bool): Whether to show all keys.

	Returns:
		If quiet is True, nothing, else either a string-joined list of lines
		showing all updates, if values were supplied, else only the keys
		and if no keys were found (e.g. if the --all-keys was passed but the
		settings dictionary is empty) the string 'Nothing to see...\n'.
	"""
	with lnk.config.Manager(which, write=True) as manager:
		# If the command option is not None, get the settings for that
		# command, otherwise we'll use settings for the which itself
		if command:
			manager = manager['commands'][command]
		manager = manager['settings']
		keys = manager.keys() if (not keys or all_keys) else keys
		keys = list(keys)
		values = list(values)

		if quiet:
			be_quiet(manager, keys, values)
		else:
			lines = [update(manager, key, values) for key in keys]
			output = '\n'.join(lines) if lines else 'Nothing to see...'

			return '{0}\n'.format(output)


def be_quiet(manager, keys, values):
	"""
	Handles the case where the quiet flag was set.

	The effective result is the same as if the quiet flag was not set,
	but it is done more efficiently because nothing needs to be formatted here.

	Arguments:
		keys (tuple): The keys.
		values (tuple): The values.
	"""
	while values:
		key = keys.pop(0)
		manager[key] = values.pop(0)


def update(manager, key, values):
	"""
	Updates the configuration and returns a formatted string for the update.

	Arguments:
		manager (config.manager.Manager): The manager instance used for
										  interacting with the configuration
										  file.
		key (str): The key to configure.
		values (tuple): The tuple of values. If not None, the first one will be
						popped out of this list and regarded as the new value
						for the key.

	Returns:
		A formatted line, following the schema
		'<key>: <old_value> => <new_value>'.
	"""
	line = '{0}: {1}'.format(key, format_value(manager[key]))
	if values:
		manager[key] = values.pop(0)
		line += ' => {0}'.format(manager[key])

	return line


def format_value(value):
	"""
	Formats a value for output.

	Arguments:
		value (?): The value to format.

	Returns:
		If the value is a list, returns a comma-separated string of the items
		in the list. If the value is a dictionary, returns a comma-separated
		string-representation of the key-value-pairs. Else returns the value,
		cast to a string.
	"""
	if isinstance(value, list):
		return ', '.join(map(str, value))
	elif isinstance(value, dict):
		return ', '.join(['{0}: {1}'.format(k, v) for k, v in value.items()])
	return str(value)
