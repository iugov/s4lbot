# -*- coding: utf-8 -*-
import logging
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append("src")

from common import log
from utils import text_processing


class TestTextProcessing(unittest.TestCase):
    @log
    def test_from_file(self):
        logging.info("Creating a temporary file...")
        temp = tempfile.NamedTemporaryFile(prefix="s4lbot_", mode="w+t")
        logging.info(f"Created file {temp.name}")

        try:
            logging.info(f"Writing text to file...")

            temp.writelines("Lorem Ipsum \nDolor Sit Amet \nConsectetur...")
            logging.info(f"Done.")

            temp.seek(0)

            logging.info(f"Reading file and comparing...")

            self.assertEqual(temp.read(), text_processing.from_file(Path(temp.name)))
            logging.info(f"File content matches.")
        finally:
            temp.close()


if __name__ == "__main__":
    unittest.main()
