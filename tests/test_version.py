"""
Tests the version number
"""
from hciw import __version__
import unittest


class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertIsInstance(__version__, str)
