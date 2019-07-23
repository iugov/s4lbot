# -*- coding: utf-8 -*-
import logging
import sys
import unittest

sys.path.append("src")

from telegram import User

from common import log
from settings import DB, DEVELOPERS
from utils import db


# logging.basicConfig(stream=sys.stderr, level=logging.INFO)


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
        logging.info("Connection succesful.")
        db.close(connection)

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

        initial_first_name = "Alpha"
        initial_last_name = "Beta"
        initial_username = "0sAD78sda9sA9K"

        user = User(
            id=123456789,
            first_name=initial_first_name,
            last_name=initial_last_name,
            username=initial_username,
            is_bot=False,
        )

        db.add_user(user)

        user.first_name = "Centauri"
        user.last_name = "Domini"
        user.username = "7s7gh2LJs7As11"

        logging.info(
            f'User {user.id} changed their first name from "{initial_first_name}" to "{user.first_name}".'
        )
        logging.info(
            f'User {user.id} changed their last name from "{initial_last_name}" to "{user.last_name}".'
        )
        logging.info(
            f'User {user.id} changed their username from "{initial_username}" to "{user.username}".'
        )

        db.update_user(user)

        result = db.lookup_user(user)
        self.assertEqual(result["fname"], user.first_name)
        self.assertEqual(result["lname"], user.last_name)
        self.assertEqual(result["username"], user.username)

        logging.info("Credentials match.")

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
