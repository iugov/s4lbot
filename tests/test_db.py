# -*- coding: utf-8 -*-
import logging
import sys
import unittest

sys.path.append("src")

from telegram import User
from settings import DB, DEVELOPERS
from common import log, get_random_tid
from utils import db


class TestDatabase(unittest.TestCase):
    @log
    def test_connect(self):
        with db.connect() as connection:
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

    @log
    def test_lookup_user(self):
        with db.connect() as connection:
            self.assertEqual(
                db.lookup_user(connection, DEVELOPERS[0])["tid"], DEVELOPERS[0]
            )
            self.assertEqual(
                db.lookup_user(connection, DEVELOPERS[1])["tid"], DEVELOPERS[1]
            )
            self.assertFalse(db.lookup_user(connection, get_random_tid(connection)))
            self.assertFalse(db.lookup_user(connection, get_random_tid(connection)))

    @log
    def test_add_user(self):
        with db.connect() as connection:
            user = User(
                id=get_random_tid(connection),
                first_name="Alpha",
                last_name="Beta",
                username="s4lbot_test",
                is_bot=False,
            )

            db.add_user(connection, user)

            result = db.lookup_user(connection, user.id)
            self.assertTrue(result)
            self.assertEqual(result["tid"], user.id)
            self.assertEqual(result["fname"], user.first_name)
            self.assertEqual(result["lname"], user.last_name)
            self.assertEqual(result["username"], user.username)

            db.delete_user(connection, user)

    @log
    def test_update_user(self):

        initial_first_name = "Alpha"
        initial_last_name = "Beta"
        initial_username = "0sAD78sda9sA9K"

        with db.connect() as connection:
            user = User(
                id=get_random_tid(connection),
                first_name=initial_first_name,
                last_name=initial_last_name,
                username=initial_username,
                is_bot=False,
            )

            db.add_user(connection, user)

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

        with db.connect() as connection:
            db.update_user(connection, user)

            result = db.lookup_user(connection, user)
            self.assertEqual(result["fname"], user.first_name)
            self.assertEqual(result["lname"], user.last_name)
            self.assertEqual(result["username"], user.username)

            db.delete_user(connection, user)

    @log
    def test_delete_user(self):
        with db.connect() as connection:
            user = User(
                id=get_random_tid(connection),
                first_name="Alpha",
                last_name="Beta",
                username="s4lbot_test",
                is_bot=False,
            )

            db.add_user(connection, user)

            result = db.lookup_user(connection, user)
            self.assertTrue(result)
            self.assertEqual(user.id, result["tid"])

            db.delete_user(connection, user)
            result = db.lookup_user(connection, user)
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
