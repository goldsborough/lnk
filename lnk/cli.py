#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""The main entry-point to lnk from the command-line."""

import click
import os
import sys

from overrides import overrides

import lnk.config
import lnk.errors

class Main(click.MultiCommand):
	"""
	The main command-group of the lnk application.

	This class exists because the necessary subcommands of lnk
	(i.e. the commands for the services, such as bitly or googl)
	live in other files and click does not handle that well. There
	is no way to register commands from other files, so this class,
	which derives from click.MultiCommand, must dynamically load
	and compile the files in which the other commands live and
	extract the necessary functions so that click can execute each
	subcommand as if it lived in this file. It also handles argument
	forwarding and some string-handling (e..g so that googl and goo.gl both
	mean the same thing from the CLI). Its all a bit of a hack.

	Attributes:
		commands (dict): A mapping between the names of commands and their
						 respective functions.
		default (str): The name of the default service (e.g. 'bitly').
	"""
	def __init__(self):
		super(Main, self).__init__(context_settings=dict(
								  ignore_unknown_options=True))
		self.commands = {}
		with lnk.config.Manager('lnk') as manager:
			self.default = manager['settings']['service']
			for command in manager['services'] + ['config']:
				command = command.replace('.', '') # goo.gl -> googl
				self.commands[command] = self.get_function(command)

	def format_usage(self, context, *args):
		# Hack to make the main script's name
		# appear as 'lnk' rather than 'main.py'
		context.info_name = 'lnk'

		return super(Main, self).format_usage(context, *args)

	@overrides
	def invoke(self, context):
		"""
		Invokes a command.

		This method does some argument pre-processing, such as inserting
		the name of the default command if no other command was specified.
		It also handles the problem of dots in the names of commands (e.g.
		goo.gl and gool).
		"""
		escaped = context.args[0].replace('.', '')
		if escaped not in self.commands.keys():
			context.args.insert(0, self.default.replace('.', ''))
		else:
			context.args[0] = escaped
		super(Main, self).invoke(context)

	@overrides
	def list_commands(self, context):
		"""Returns the names of all available subcommands."""
		return self.commands.keys()

	@overrides
	def get_command(self, context, name):
		"""Returns the function for a given subcommand-name."""
		if name not in self.commands:
			clue = lnk.errors.Message('Did you mess up the default settings?',
									  level=0)
			try_message = lnk.errors.Message("See what 'lnk config -k service'"
									  		 " says.", level=1)
			raise lnk.errors.UsageError('Invalid default service.',
										Clue=clue,
										Try=try_message)
		return self.commands[name]

	@staticmethod
	def get_function(service):
		"""
		Returns the 'main' command-function for a given service.

		Arguments:
			service (str): The name of the service (e.g. tinyurl).

		Returns:
			The main() function of that service (retrieved from
			lnk.<service>.cli).
		"""
		namespace = {}
		directory = os.path.dirname(__file__)
		filename = os.path.join(directory, service, 'cli.py')
		with open(filename) as source:
			code = compile(source.read(), filename, 'exec')
			eval(code, namespace, namespace)

		return namespace['main']

def get_verbosity(count, level):
	"""
	Returns the appropriate verbosity level.

	Defined here for use by all cli modules (e.g. bitly.cli).

	Arguments:
		count (int): The verbosity count (from the -vvv flags).
		level (int): The verbosity level (from the --level flag).

	Returns:
		The default verbosity if both count and level are zero, else
		the level and only if the level is also zero, the count.
	"""
	if count == 0 and not level:
		return lnk.config.get('lnk', 'settings')['verbosity']
	elif level:
		return level
	return count

def main():
	"""
	Insantiates a Main object and executes it.

	The 'standalone_mode' is so that click doesn't handle usage-exceptions
	itself, but bubbles them up.

	Arguments:
		args (tuple): The command-line arguments.
	"""
	args = sys.argv[1:]
	# If stdin is not empty (being piped to)
	if not sys.stdin.isatty():
		args += sys.stdin.readlines()
	command = Main()
	catch = lnk.errors.Catch(1)
	catch.catch(command.main, args, standalone_mode=False)

if __name__ == '__main__':
	main()
