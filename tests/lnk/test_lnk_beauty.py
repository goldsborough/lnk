#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ecstasy
import pytest

import tests.paths

import lnk.beauty

@pytest.fixture(scope='module')

def fixture():
	leg = ecstasy.beautify('<leg>', ecstasy.Style.Blink | ecstasy.Color.Blue)
	return [[leg, 'grapefruit'], ['hippopotamus']]


def test_max_width_60_if_no_terminal():
	assert lnk.beauty.MAX_WIDTH == 60

	# What we'll use for testing
	lnk.beauty.MAX_WIDTH = 10


def test_escape_escapes_well(fixture):
	result = lnk.beauty.escape(fixture[0][0])

	assert isinstance(result, tuple)
	assert result.raw == fixture[0][0]
	assert result.escaped == 'leg'


def test_escape_leaves_strings_w_o_escape_codes_alone(fixture):
	result = lnk.beauty.escape(fixture[0][1])

	assert isinstance(result, tuple)
	assert result.raw == fixture[0][1]
	assert result.escaped == fixture[0][1]


def test_get_escaped_escapes_results_well(fixture):
	result, _ = lnk.beauty.get_escaped(fixture)
	expected = [[lnk.beauty.escape(j) for j in i] for i in fixture]

	assert result == expected


def test_get_escaped_picks_correct_width(fixture):
	_, width = lnk.beauty.get_escaped([fixture[0]])

	assert width == len('grapefruit')


def test_get_escaped_truncates_to_max_width(fixture):
	_, width = lnk.beauty.get_escaped(fixture)

	assert width == lnk.beauty.MAX_WIDTH


def test_ljust_works_well(fixture):
	line = lnk.beauty.escape(fixture[0][0])
	adjusted = lnk.beauty.ljust(line, 10)
	expected = '{0}{1}'.format(fixture[0][0], ' ' * 7)

	assert adjusted == expected


def test_wrap_works_well(fixture):
	line = lnk.beauty.escape(fixture[0][0])
	wrapped = [i.escaped for i in lnk.beauty.wrap(line, 2)]

	assert len(wrapped) == 2
	assert not any(len(i) > 10 for i in wrapped)
	assert wrapped == ['le', ' g']


def test_boxify_works_well(fixture):
	lines = [lnk.beauty.escape(j) for i in fixture for j in i]
	border = '─' * (lnk.beauty.MAX_WIDTH + 2)
	wrapped = lnk.beauty.wrap(lines[2], lnk.beauty.MAX_WIDTH)
	width = lnk.beauty.MAX_WIDTH
	expected = [
		'┌{0}┐'.format(border),
		'│ {0} │'.format(lnk.beauty.ljust(lines[0], width)),
		'│ {0} │'.format(lnk.beauty.ljust(lines[1], width)),
		'├{0}┤'.format(border),
		'│ {0} │'.format(lnk.beauty.ljust(wrapped[0], width)),
		'│ {0} │'.format(lnk.beauty.ljust(wrapped[1], width)),
		'└{0}┘'.format(border)
	]
	print(fixture)
	box = lnk.beauty.boxify(fixture)
	print(box)
	assert box == '\n'.join(expected)
