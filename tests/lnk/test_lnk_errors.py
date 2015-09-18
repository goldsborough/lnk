#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import ecstasy
import pytest
import requests

import tests.paths
import lnk.errors


def test_verbosity_system_works_without_additional():
	what = 'something happened'
	error = lnk.errors.Error(what)
	typ = ecstasy.beautify('<Type>: Error', ecstasy.Color.Red)

	assert error.what == what
	assert error.levels[2] == typ


def test_get_levels_works():
	error = lnk.errors.Error('something happened')

	assert len(error.levels) == 4
	assert any(error.levels)
	assert not error.levels[1]
	assert not error.levels[3]
	assert 'Error' in error.levels[0]
	assert 'Type' in error.levels[2]


def test_verbosity_system_works_with_additional():
	foo = lnk.errors.Message(what='foo?', level=1)
	bar = lnk.errors.Message(what='bar!', level=3)
	error = lnk.errors.Error('something happened', Foo=foo, Bar=bar)

	assert len(error.levels) == 4
	assert all(error.levels)
	assert 'Foo' in error.levels[1]
	assert 'foo?' in error.levels[1]
	assert 'Bar' in error.levels[3]
	assert 'bar!' in error.levels[3]


def test_catch_catches_lnk_error(capsys):
	def throws():
		raise lnk.errors.Error('oops')
	lnk.errors.catch(throws)
	captured = capsys.readouterr()

	assert captured
	assert 'Error' in captured[0]
	assert 'oops' in captured[0]


def test_catch_shows_only_wanted_levels_for_verbosity_0(capsys):
	catch = lnk.errors.Catch()
	def throws():
		raise lnk.errors.Error('oops')
	catch.catch(throws)
	captured = capsys.readouterr()

	assert captured

	levels = [i for i in captured[0].split('\n') if i]

	assert len(levels) == 1
	assert 'Error' in levels[0]
	assert 'oops' in levels[0]


def test_catch_shows_all_levels_for_verbosity_4(capsys):
	catch = lnk.errors.Catch(3)
	def throws():
		foo = lnk.errors.Message(what='foo?', level=1)
		bar = lnk.errors.Message(what='bar!', level=3)
		raise lnk.errors.InternalError('oops', Foo=foo, Bar=bar)
	catch.catch(throws)
	captured = capsys.readouterr()

	assert captured

	levels = [i for i in captured[0].split('\n') if i]

	assert len(levels) == 4
	assert 'Error' in levels[0]
	assert 'oops' in levels[0]
	assert 'Foo' in levels[1]
	assert 'foo?' in levels[1]
	assert 'Type' in levels[2]
	assert 'InternalError' in levels[2]
	assert 'Bar' in levels[3]
	assert 'bar!' in levels[3]


def test_catch_catches_click_exception(capsys):
	catch = lnk.errors.Catch(2)
	def throws():
		raise click.ClickException('')
	catch.catch(throws)
	captured = capsys.readouterr()

	assert captured

	levels = [i for i in captured[0].split('\n') if i]

	assert 'Error' in levels[0]
	assert 'Type' in levels[1]
	assert 'UsageError' in levels[1]


def test_catch_catches_requests_exception(capsys):
	catch = lnk.errors.Catch(2)
	def throws():
		raise requests.exceptions.ConnectionError
	catch.catch(throws)
	captured = capsys.readouterr()

	assert captured

	levels = [i for i in captured[0].split('\n') if i]

	assert 'Error' in levels[0]
	assert 'Type' in levels[2]
	assert 'ConnectionError' in levels[2]


def test_catch_bubbles_up_other_exceptions():
	catch = lnk.errors.Catch()
	def throws():
		raise RuntimeError

	with pytest.raises(RuntimeError):
		catch.catch(throws)


def test_warn_works(capsys):
	lnk.errors.warn('Sauron is coming')
	captured = capsys.readouterr()

	assert captured
	assert 'Warning' in captured[0]
	assert '\a' in captured[0]
	assert 'Sauron is coming' in captured[0]
