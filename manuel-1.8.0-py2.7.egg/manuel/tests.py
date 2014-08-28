from __future__ import absolute_import

import doctest
import manuel
import manuel.capture
import manuel.codeblock
import manuel.doctest
import manuel.ignore
import manuel.testcase
import manuel.testing
import os.path
import re
import unittest
import zope.testing.renormalizing

here = os.path.dirname(os.path.abspath(__file__))

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r"<unittest\.result\.TestResult"), '<unittest.TestResult'),
    # PyPy spells some error messages differently
    (re.compile(r"NameError: global name '([a-zA-Z0-9_]+)' is not defined"),
     r"NameError: name '\1' is not defined"),
    # PyPy's default __repr__ is slightly different
    (re.compile(r"<__builtin__\.(Table|TableError|NumbersTest|NumbersResult) object"),
     r"<\1 object"),
    (re.compile(r"<SRE_Match object"),
     r"<_sre.SRE_Match object"),
])


def turtle_on_the_bottom_test():
    """We use manuel to test itself.

    This means that if we completely hose manuel, we might not
    know. Use doctest to do a basic sanity check.

    >>> document = manuel.Document('''This is my doctest.
    ...
    ...     >>> 2 + 2
    ...     5
    ... ''')
    >>> document.process_with(manuel.doctest.Manuel(), globs={})
    >>> print(document.formatted())
    File "<memory>", line 3, in <memory>
    Failed example:
        2 + 2
    Expected:
        5
    Got:
        4
    <BLANKLINE>

    """

def test_suite():
    tests = ['index.txt', 'table-example.txt', 'README.txt', 'bugs.txt',
        'capture.txt']

    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

    m = manuel.ignore.Manuel()
    m += manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    m += manuel.codeblock.Manuel()
    m += manuel.capture.Manuel()
    m += manuel.testcase.SectionManuel()
    # The apparently redundant "**dict()" is to make this code compatible with
    # Python 2.5 -- it would generate a SyntaxError otherwise.
    suite = manuel.testing.TestSuite(m, *tests, **dict(
        globs={'path_to_test': os.path.join(here, 'bugs.txt')}))


    return unittest.TestSuite((
        suite,
        doctest.DocTestSuite(),
        ))
