#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

TEST_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(TEST_PATH)
CONFIG_PATH = os.path.join(ROOT_PATH, 'config')
LNK_PATH = os.path.join(ROOT_PATH, 'lnk')

sys.path.insert(0, ROOT_PATH)
sys.path.insert(0, LNK_PATH)
