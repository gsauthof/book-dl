#!/usr/bin/env python3

import unittest
import sys
import test.epub
import test.gb_de

#unittest.main(argv=[sys.argv[0], 'test.epub', 'test.gb_de'])

unittest.main(module=None, argv=[sys.argv[0], 'discover',
    '--start-directory', 'test', '--pattern', '*.py',
    '--top-level-directory', '.'])
