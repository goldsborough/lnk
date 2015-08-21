#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from lnk.errors import Error

class InvalidKeyError(Error):
	def __init__(self, what):
		super(InvalidKeyError, self).__init__(what)

