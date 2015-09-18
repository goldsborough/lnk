***
lnk
***

* `Introduction`_

* `Usage`_

* `bit.ly`_

* `goo.gl`_

* `tinyurl`_

* `config`_

* `Source Code`_

Introduction
============

**lnk** is URL-shortening client that currently supports three services: `bit.ly <http://bit.ly>`_, `goo.gl <http://goo.gl>`_ and `tinyurl <http://tinyurl.com>`_. Essentially, **lnk** is a collection of separate command-line utilities for each of these services, however the interfaces to them are largely the same so that you can easily switch between them. Note, however, that not all services provide the same information or have the same functionality. For example, for bit.ly, you can not only manipulate short and long links, but also access metrics about links and also information about your user-profile. At the same time, goo.gl provides similar functionality as bit.ly, however it has no concept of a 'user-profile', so you cannot retrieve information about yourself. tinyurl is the retarded child among the three, it can only shorten links. In the sub-sections below you can find full lists of all functionality provided by each of the three currently-supported services.

Usage
=====

Services
--------

The lnk command-line utility is structured into a set of sub-commands for each of its services, as well as one for configuration of settings. You can see a list of available sub-commands simply by typing :code:`$ lnk`, which is equivalent to :code:`$ lnk --help`:

.. note::
	
	This is true for all commands of *lnk*: typing the command alone does not execute anything, but is interpreted as a call for help and is thus equivalent to passing the *--help* flag.

.. code-block:: bash

	$ lnk
	Usage: main.py [OPTIONS] COMMAND [ARGS]...

	Options:
	  --help  Show this message and exit.

	Commands:
	  bitly    bit.ly command-line client.
	  tinyurl  tinyurl command-line client.
	  config   Configuration interface.
	  googl    goo.gl command-line client.

However you need not specify the service you wish to use every time you use lnk, as its configuration-system allows for default-settings (refer to the `config`_ section for more information). One such default-setting is your default *service*, which lnk will always use if you omit the service sub-command. If your current default-service is bit.ly, :code:`$ lnk ...` is equivalent to typing :code:`$ lnk bitly ...`.

.. note::
	
	You can type "bit.ly" or "bitly", "goo.gl" or "googl" to specify the respective command.

Commands
--------

Each such sub-command (for each URL-shortening service + config) is further structured into a set of commands which perform some specific task, such as shortening lnks or retrieving statistics for a link. This is where the services differ, as they do not all provide the same set of commands. bit.ly is the most complete and you can see what commands it supplies by typing :code:`$ lnk bitly` or :code:`$ lnk bitly --help`:

.. code-block:: bash

	$ lnk bitly --help
	Usage: lnk bitly [OPTIONS] [ARGS]... COMMAND [ARGS]...

	  bit.ly command-line client.

	Options:
	  -v, --verbose  Controls the level of verbosity (in case of exceptions).
	  --version      Show the version and exit.
	  --help         Show this message and exit.

	Commands:
	  history  Retrieve link history.
	  info     Information about links.
	  key      Generate an API key for user metrics and...
	  link     Link shortening and expansion.
	  stats    Statistics and metrics for links.
	  user     Show meta-information for the current user.

Options & Arguments
-------------------

Each command takes, of course, further options and arguments, which you can see by typing :code:`$ lnk <service> <command>`. For example, here's the usage information for bitly's *link* command:

.. code-block:: bash

	$ lnk bitly link --help
	Usage: main.py [OPTIONS] [URLS]...

	  Link shortening and expansion.

	Options:
	  -c, --copy / -n, --no-copy  Whether or not to copy the first link to the
	                              clipboard.
	  -q, --quiet / -l, --loud    Whether or not to print warnings.
	  -e, --expand URL            Expand a short url (bitlink).
	  -s, --shorten URL           Shorten a long url.
	  --pretty / --plain          Whether to show the links in a pretty box or as a plain list.
	  --help                      Show this message and exit.


Verbosity
---------

lnk has a special verbosity system that controls how much information you see when an exception is thrown. There are four levels of verbosity, where the first level will always show the error message and the third level the (Python) type. What the other levels show depends on the context of the exception, so you will have to just increment the level to see if more information is available.

There are two ways to manipulate the level of verbosity:

1. Passing the :code:`-v` multiple times. The default level already is 1, so passing :code:`-v` increments the verbosity level to 2.

2. Passing the :code:`-l` or :code:`--level` flag, which takes as its argument the level of verbosity you wish to specify. Level 0 means the default level will be taken, which you can configure in the default settings of lnk.

.. note::

	The verbosity must be passed passed to the sub-commands for each service + config, i.e. :code:`$ lnk bitly -vv link ...` is valid, while :code:`lnk -vv bitly link` or :code:`$ lnk bitly link -vv` are ill-formed commands.

bit.ly
======

The bit.ly (or "bitly") command interfaces with the bit.ly API and provides the following functionality:

.. code-block:: bash

	Usage: lnk bitly [OPTIONS] [ARGS]... COMMAND [ARGS]...

	  bit.ly command-line client.

	Options:
	  -v, --verbose        Increments the level of verbosity.
	  -l, --level INTEGER  Controls the level of verbosity.
	  --version            Show the version and exit.
	  --help               Show this message and exit.

	Commands:
	  history  Retrieve link history.
	  info     Information about links.
	  key      Authorization management.
	  link     Link shortening and expansion.
	  stats    Statistics and metrics for links.
	  user     Show meta-information for the current user.


Authorization
-------------

The bitly command requires authorization to access user-sensitive data such as link history. For this, the :code:`key` command exists, which you must call once before being able to perform any actions with the bit.ly service. There are two ways to use this command, as you can see in its usage:

.. code-block:: bash

	Usage: lnk [OPTIONS]

	  Authorization management.

	Options:
	  -g, --generate           Generate a new api key (asks for login/password).
	  -l, --login TEXT         Generate a new api key with this login.
	  -p, --password TEXT      Generate a new api key with this password.
	  -s, --show / -h, --hide  Whether to show or hide the generated API key.
	  -w, --who                Show who is currently logged in.
	  --help                   Show this message and exit.

The first, easiest and safest way is to execute :code:`$ lnk bitly key --generate`, which will prompt you for your login and password. The second way is to pass those two items in the command directly, like so: :code:`$ lnk bitly key --login <your_bitly_login> --password <your_bitly_password>`. The first way is safer because the password prompt hides the input, so if a hacker is looking over your shoulder he or she will not see your password and find out what naughty links you've been shortening.

goo.gl
======

The goo.gl command interfaces with the goo.gl API and provides almost just as much functionality as the bit.ly command, with the exception of the :code:`user` command, which does not exist for goo.gl (the API provides no information about the account connected to given credentials). Here is the usage for the goo.gl command:

.. code-block:: bash

	Usage: lnk googl [OPTIONS] [ARGS]... COMMAND [ARGS]...

	  goo.gl command-line client.

	Options:
	  -v, --verbose        Increments the level of verbosity.
	  -l, --level INTEGER  Controls the level of verbosity.
	  --version            Show the version and exit.
	  --help               Show this message and exit.

	Commands:
	  history  Retrieve link history.
	  info     Information about links.
	  key      Authorization management.
	  link     Link shortening and expansion.
	  stats    Statistics and metrics for links.


Authorization
-------------

The authorization-procedure for goo.gl is rather special, as it doesn't all happen on the command-line. When you execute :code:`$ lnk googl key --generate`, which you must do before anything else when first using lnk with goo.gl, your default web-browser is opened on a page asking you to authorize lnk to access your information. When you accept, you are shown an access-token which you then have to paste into lnk, which expects this token and shows an appropriate prompt for it.

tinyurl
=======

The tinyurl command allows you to shorten links with tinyurl. The service itself is quite simple and provides only this functionality, so that is also the only thing you can do when you execute this command, as can be seen from its usage string:

.. code-block:: bash

	Usage: lnk tinyurl [OPTIONS] [ARGS]... COMMAND [ARGS]...

	  tinyurl command-line client.

	Options:
	  -v, --verbose        Increments the level of verbosity.
	  -l, --level INTEGER  Controls the level of verbosity.
	  --version            Show the version and exit.
	  --help               Show this message and exit.

	Commands:
	  link  Link shortening.

Authorization
-------------

The tinyurl command requires no authorization.

config
======

lnk includes a configuration-management-system that allows you to keep and modify default settings for the application itself, for the services and for all of their commands. This configuration-management-system can be accessed via the :code:`config` command, whose usage looks as follows:

.. code-block:: bash

	Usage: lnk config [OPTIONS] [WHICH] [COMMAND]

	  Configuration interface.

	Options:
	  -k, --key KEY             A key to show or manipulate.
	  -v, --value VALUE         A new value for a key.
	  -q, --quiet / -l, --loud  Whether to visualize changes.
	  -a, --all, --all-keys     Whether to show all keys.
	  --help                    Show this message and exit.

You can access settings of the bitly, googl or tinyurl services as well as for lnk itself (such as the default service) and also the config command by typing :code:`lnk config <which>`. For the services (bitly, googl and tinyurl), you can also specify a command for which to configure settings, e.g. :code:`lnk config googl link` would give you access to the settings for the googl/goo.gl's :code:`link` command. If you provide no value for *which*, it is assumed you wish to modify the configuration of *lnk*. In general, any setting is characterized by a key and a value, e.g. the key for lnk's default service would be "service" and the value for example "tinyurl".

To display settings, you can then either pass the :code:`-a/--all/--all-keys` flag, which will show you all available keys, or specify them by their name using the :code:`-k, --key` option. This will *only show* you the keys. To change the value of a key, you have to supply a new value with the :code:`-v, --value` option. The keys and values are mapped to each other in order of their appearance, i.e. for a command such as :code:`lnk config bitly -k <a> -v 1 -k <b> -v 2 `, the first key '<a>' (not a real key, just for proof of concept)  will be given the first value 1 and the second key '<b>' is given the value 2. This mapping-system means the above command is equivalent to this command: :code:`lnk config bitly -k <a> -k <b> 1 2`. Any remaining keys without a value  are only displayed.

.. note::

	You cannot add settings. If the argument to :code:`-k` is not found in the settings you wish to modify, an exception is raised.

Example
-------

Here is how you would change the default service using this configuration system. First, see which keys are available for lnk and what their values are:

.. code-block:: bash

	$ lnk config lnk --all
	verbosity: 0
	copy: True
	service: googl

Which you can also do like this:

.. code-block:: bash

	$ lnk config lnk -k verbosity -k copy -k service
	verbosity: 0
	copy: True
	service: googl

Then, pass a new value for the "service" key:

.. code-block:: bash

	$ lnk config lnk -k service -v bitly
	service: googl => bitly

Now when you access :code:`link`, :code:`stats` or any other command without explicitly stating the service, this will be for bitly rather than googl. Had you not wanted to plague yourself with that output, you could have asked lnk to keep quiet about its changes with the :code:`-q/--quiet` flag (whose default value you can also change in the :code:`config` command's settings):

.. code-block:: bash

	$ lnk config lnk -q -k service -v bitly

Source Code
===========

You can find documentation for **lnk**'s source-code `here <modules.html>`_:
