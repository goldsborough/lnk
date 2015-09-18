***
lnk
***

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square
 :target: http://goldsborough.mit-license.org

.. image:: http://img.shields.io/gratipay/goldsborough.svg?style=flat-square
 :target: https://gratipay.com/~goldsborough/

A command-line URL-shortening client for bitly, tinyurl and goo.gl.

How a smart dev (you) shortens a URL:

.. image:: https://goo.gl/Y5eCsd

But **lnk** is *MORE*. **lnk** can also expand short URLs:

.. code-block:: bash

	$ lnk -e http://bit.ly/1NWAPWn
	┌─────────────────────────────────────────────┐
	│ http://bit.ly/1NWAPWn => http://google.com/     │
	└─────────────────────────────────────────────┘

Get all sorts of awesome stats and metrics for a URL:

.. code-block:: bash

	$ lnk stats -i http://bit.ly/1NWAPWn
	┌───────────────────────────────┐
	│ URL: http://bit.ly/1EHdqZq       │
	│ Referrers:                       │
	│  + Since forever:                │
	│    - Direct: 503                 │
	│    - http://bit.ly/1EHdqZq: 1    │
	│ Clicks:                          │
	│  + Since forever: 504            │
	│ Countries:                       │
	│  + Since forever:                │
	│    - United States: 197          │
	│    - United Kingdom: 50          │
	│    - Germany: 45                 │
	│    - France: 27                  │
	│    - Canada: 20                  │
	│    - Netherlands: 16             │
	│    - Russian Federation: 12      │
	│    - Australia: 11               │
	│    - Spain: 10                   │
	│    - Brazil: 9                   │
	└───────────────────────────────┘

Tell you about yourself:

.. code-block:: bash

	$ lnk user -a
	┌────────────────────────────────────────────────────┐
	│ Full Name: Peter Goldsborough                           │
	│ Login: goldsborough                                     │
	│ Member Since: Wed Aug 26 13:57:00 2015                  │
	│ Link privacy: public                                    │
	│ ...                                                     │
	└────────────────────────────────────────────────────┘

And what you've been up to:

.. code-block:: bash

	$ lnk history --last 4 days
	┌────────────────────────────┐
	│ Last 4 days:                  │
	│  + http://bit.ly/1OQM9nA      │
	│  + http://bit.ly/1Km6CB1      │
	│  + http://bit.ly/1OQLTov      │
	│  + http://on.fb.me/1OQHeD0    │
	└────────────────────────────┘


**lnk** is your fast, complete and sweet destination for shortening URLs and everything connected to it.

Installation
============

Whoop:

.. code-block:: bash

	$ pip install lnk

dee-doo.

`Documentation <http://lnk.rtfd.org/>`_
=======================================

Documentation for the project's source alongside a detailed description of how to effectively use **lnk** can be found `here <http://lnk.rtfd.org/>`_.

`License <http://goldsborough.mit-license.org>`_
================================================

**lnk** is released under the `MIT License <http://goldsborough.mit-license.org>`_.

Authors
=======

Peter Goldsborough & `cat <https://goo.gl/IpUmJn>`_ :heart:
