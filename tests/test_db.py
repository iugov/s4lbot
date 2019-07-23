# -*- coding: utf-8 -*-
import sys
import unittest
import logging
from telegram import User

sys.path.append("src")

from functools import wraps
from settings import DB, DEVELOPERS
from utils import db

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def log(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        logging.info(f"Testing {func.__name__} ...")
        return func(*args, **kwargs)

    return with_logging


class TestDatabase(unittest.TestCase):
    @log
    def test_connect(self):
        connection = db.connect()
        self.assertEqual(
            connection.get_dsn_parameters(),
            {
                "user": DB["user"],
                "dbname": DB["name"],
                "host": DB["host"],
                "port": DB["port"],
                "tty": "",
                "options": "",
                "sslmode": "prefer",
                "sslcompression": "0",
                "krbsrvname": DB["krbsrvname"],
                "target_session_attrs": "any",
            },
        )
        connection.close()
        logging.debug("DB connection -")

    @log
    def test_lookup_user(self):
        for tid in DEVELOPERS:
            result = db.lookup_user(tid)
            self.assertEqual(result["tid"], tid)

    @log
    def test_add_user(self):
        user = User(
            id=123456789,
            first_name="Alpha",
            last_name="Beta",
            username="s4lbot_test",
            is_bot=False,
        )
        db.add_user(user)

        result = db.lookup_user(user.id)

        self.assertTrue(result)
        self.assertEqual(result["tid"], user.id)
        self.assertEqual(result["fname"], user.first_name)
        self.assertEqual(result["lname"], user.last_name)
        self.assertEqual(result["username"], user.username)
        # TODO: Add 'created' field check.

        db.delete_user(user)

    @log
    def test_update_user(self):
        user = User(
            id=123456789,
            first_name="Alpha",
            last_name="Beta",
            username="s4lbot_test",
            is_bot=False,
        )

        db.add_user(user)

        user.first_name = "Centauri"
        user.last_name = "Domini"
        user.username = "Ester"

        db.update_user(user)

        result = db.lookup_user(user)
        self.assertEqual(result["fname"], "Centauri")
        self.assertEqual(result["lname"], "Domini")
        self.assertEqual(result["username"], "Ester")

        db.delete_user(user)

    @log
    def test_delete_user(self):
        user = User(
            id=123456789,
            first_name="Alpha",
            last_name="Beta",
            username="s4lbot_test",
            is_bot=False,
        )
        db.add_user(user)
        result = db.lookup_user(user)
        self.assertTrue(result)
        self.assertEqual(user.id, result["tid"])

        db.delete_user(user)
        result = db.lookup_user(user)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
