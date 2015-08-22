#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Service(object):

	__metaclass__ = ABCMeta

	@abstractmethod
	def run():
		raise NotImplementedError

	@abstractmethod
	def link():
		raise NotImplementedError

	@abstractmethod
	def info():
		raise NotImplementedError

	@abstractmethod
	def stats():
		raise NotImplementedError

	@abstractmethod
	def user():
		raise NotImplementedError
