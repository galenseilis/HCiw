"""
Tests the version number
"""

import unittest

from hciw import __version__


class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertIsInstance(__version__, str)
