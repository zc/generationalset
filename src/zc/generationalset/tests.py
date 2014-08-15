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

def no_duck_typing():
    """Duck typing is for quacks

    We'd foolishly imagined that objects could play with the internal
    gset collaborations by implementing a few messages.  This tuened
    out to be a bit silly. Worse, it's not uncommon for an object that
    uses generational sets to implement ``generational_updates``:

    >>> import zc.generationalset
    >>> class C:
    ...     id = ''
    ...     def __init__(self):
    ...         self.changes = zc.generationalset.GSet()
    ...         self.changes.add(self)
    ...     def generational_updates(self, generation):
    ...         return self.changes.generational_updates(self)
    >>> c = C() # When we used hasattr, rather than isinstance, this blew up
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.txt'),
        ))

