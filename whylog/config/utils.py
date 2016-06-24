IMPORTED_RE = False

try:
    import regex
except ImportError:
    import re as regex
    IMPORTED_RE = True
    # This handling of import regex error does not really mean that
    # we are able to work without regex being installed. It means that
    # whylog can work with these python versions, which don't handle
    # regex module(like pypy, pypy3). So if you use cpython 2.5-3.5
    # please install regex module. That will improve whylog performance.

assert regex


class CompareResult(object):
    LT, EQ, GT = -1, 0, 1
