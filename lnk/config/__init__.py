#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os.path

from .manager import Manager, get

CONFIG_PATH = os.path.join(
	os.path.abspath(
		os.path.dirname(
			os.path.dirname(
				os.path.dirname(
					os.path.abspath(__file__)
				)
			)
		)
	),
	'config'
)
