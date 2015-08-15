#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import json

def get(config):
	return json.loads(open("config/{0}.json".format(config)).read())
