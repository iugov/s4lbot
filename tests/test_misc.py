# -*- coding: utf-8 -*-
import sys
import unittest

sys.path.append("src")

from common import log
from utils import misc


class TestMisc(unittest.TestCase):
    @log
    def test_get_title(self):
        self.assertEqual(misc.get_title("example.com"), "example.com")
        self.assertEqual(misc.get_title("www.example.com"), "www.example.com")
        self.assertEqual(misc.get_title("http://www.example.com"), "Example Domain")
        self.assertEqual(misc.get_title("https://www.example.com"), "Example Domain")
        self.assertEqual(misc.get_title("example.inv"), "example.inv")
        self.assertEqual(
            misc.get_title("https://www.example.qwq"), "https://www.example.qwq"
        )


if __name__ == "__main__":
    unittest.main()
