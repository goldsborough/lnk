#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import config

from abstract import AbstractCommand

class Command(AbstractCommand):
	def __init__(self, which):
		super(Command, self).__init__('bitly', which)
		with config.Manager('bitly') as manager:
			self.parameters = {'access_token': manager['key']}