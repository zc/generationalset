##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest
import unittest
import manuel.capture
import manuel.doctest
import manuel.testing

def ids_do_no_harm():
    """
    >>> import zc.generationalset
    >>> set = zc.generationalset.GSet("test")
    >>> set.add(1, 1)
    >>> set.generational_updates(0)
    {'generation': 2, 'adds': [1]}

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.txt'),
        ))

