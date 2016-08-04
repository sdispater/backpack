# -*- coding: utf-8 -*-

import sys
import warnings
import functools

PY2 = sys.version_info[0] == 2
PY3K = sys.version_info[0] >= 3
PY33 = sys.version_info >= (3, 3)

if PY2:
    import imp

    long = long
    unicode = unicode
    basestring = basestring

    reduce = reduce
else:
    long = int
    unicode = str
    basestring = str

    from functools import reduce


from .helpers import value, data_get, mkdir_p
