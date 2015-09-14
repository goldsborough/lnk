#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import Queue
import requests
import threading

from collections import namedtuple

import tests.paths
import bitly.info

VERSION = 3
API = 'https://api-ssl.bitly.com/v{0}'.format(VERSION)
with open(os.path.join(tests.paths.TEST_PATH, 'bitly', 'token')) as source:
	ACCESS_TOKEN = source.read()

LOCK = threading.Lock()
QUEUE = Queue.Queue()


@pytest.fixture(scope='module')
def fixture():
	