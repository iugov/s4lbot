# -*- coding: utf-8 -*-
import logging
import sys
import unittest
from datetime import datetime

sys.path.append("src")

from telegram import User
from settings import DB, DEVELOPERS
from common import log, get_random_id
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
                db.lookup_user(connection, DEVELOPERS[0]).id, DEVELOPERS[0]
            )
            self.assertFalse(db.lookup_user(connection, get_random_id(connection)))
            self.assertFalse(db.lookup_user(connection, get_random_id(connection)))

    @log
    def test_add_user(self):
        with db.connect() as connection:
            timestamp = datetime.now()
            user = User(
                id=get_random_id(connection),
                first_name="Augustus",
                is_bot=False,
                joined_on=timestamp,
            )

            db.add_user(connection, user, timestamp)

            result = db.lookup_user(connection, user.id)
            self.assertTrue(result)
            self.assertEqual(result.id, user.id)
            self.assertEqual(result.first_name, user.first_name)
            self.assertEqual(result.joined_on.ctime(), timestamp.ctime())

            db.delete_user(connection, user.id)

    @log
    def test_update_user(self):
        with db.connect() as connection:
            uid = get_random_id(connection)
            user = User(id=uid, first_name="Augustus", is_bot=False)

            db.add_user(connection, user, datetime.utcnow())

            updated_user = User(id=uid, first_name="Filamentis", is_bot=False)

            db.update_user(connection, updated_user, user.id)

            result = db.lookup_user(connection, user.id)
            self.assertEqual(result.id, updated_user.id)
            self.assertEqual(result.first_name, updated_user.first_name)

            db.delete_user(connection, user.id)

    @log
    def test_delete_user(self):
        with db.connect() as connection:
            user = User(
                id=get_random_id(connection), first_name="Augustus", is_bot=False
            )

            db.add_user(connection, user, datetime.utcnow())

            db.delete_user(connection, user.id)

            result = db.lookup_user(connection, user.id)
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
