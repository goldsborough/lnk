#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

_here = os.path.abspath(__file__)

ROOT_PATH = os.path.dirname(os.path.dirname(_here))
CONFIG_PATH = os.path.join(ROOT_PATH, 'config')
LNK_PATH = os.path.join(ROOT_PATH, 'lnk')

sys.path.insert(0, ROOT_PATH)
sys.path.insert(0, LNK_PATH)
