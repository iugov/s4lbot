# -*- coding: utf-8 -*-
import sys
import unittest

sys.path.append("src")

from common import log
from utils import misc


class TestMisc(unittest.TestCase):
    @log
    def test_get_title(self):
        expected_title = "Example Domain"
        self.assertEqual(misc.get_title("example.com"), expected_title)
        self.assertEqual(misc.get_title("www.example.com"), expected_title)
        self.assertEqual(misc.get_title("http://www.example.com"), expected_title)
        self.assertEqual(misc.get_title("https://www.example.com"), expected_title)


if __name__ == "__main__":
    unittest.main()
