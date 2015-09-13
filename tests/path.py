#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def insert():
	here = os.path.abspath(__file__)
	root = os.path.dirname(os.path.dirname(here))

	sys.path.insert(0, root)
	sys.path.insert(0, os.path.join(root, 'lnk'))