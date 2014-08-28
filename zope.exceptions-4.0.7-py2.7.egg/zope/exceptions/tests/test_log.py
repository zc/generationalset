##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""log.Formatter tests.
"""
import unittest


class FormatterTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.exceptions.log import Formatter
        return Formatter

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_simple_exception(self):
        import traceback
        tb = DummyTB()
        tb.tb_frame = DummyFrame()
        exc = ValueError('testing')
        fmt = self._makeOne()
        result = fmt.formatException((ValueError, exc, tb))
        lines = result.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 'Traceback (most recent call last):')
        self.assertEqual(lines[1], '  File "dummy/filename.py", line 14, '
                                   'in dummy_function')
        self.assertEqual(lines[2],
                        traceback.format_exception_only(
                                        ValueError, exc)[0][:-1]) #trailing \n


class DummyTB(object):
    tb_lineno = 14
    tb_next = None


class DummyFrame(object):
    f_lineno = 137
    f_back = None
    def __init__(self):
        self.f_locals = {}
        self.f_globals = {}
        self.f_code = DummyCode()

class DummyCode(object):
    co_filename = 'dummy/filename.py'
    co_name = 'dummy_function'
