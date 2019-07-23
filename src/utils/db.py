# -*- coding: utf-8 -*-
import logging
import sys

import psycopg2
import psycopg2.extras

sys.path.append("src")

from settings import DB
from telegram import User
from datetime import datetime, timezone


def connect():
    connection = psycopg2.connect(
        user=DB["user"],
        password=DB["passwd"],
        host=DB["host"],
        port=DB["port"],
        database=DB["name"],
    )
    logging.debug("DB connection +")
    return connection


# TODO: Make this more elegant.
def lookup_user(user):
    if isinstance(user, User):
        tid = user.id
    elif isinstance(user, int):
        tid = user

    connection = connect()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    logging.info(f"Looking for user {tid} ...")

    cursor.execute("SELECT * FROM users WHERE tid=%s", (tid,))
    results = cursor.fetchone()

    if results:
        logging.info(f"Found user {tid}.")
    else:
        logging.info(f"User not found.")

    cursor.close()
    connection.close()
    logging.debug("DB connection +")
    return results


def add_user(user: User):
    connection = connect()
    cursor = connection.cursor()

    # FIXME: This can be simplified.
    if lookup_user(user):
        logging.warning(f"User {user.id} already exists. Skipping.")
        cursor.close()
        connection.close()
        logging.debug("DB connection +")
        return

    cursor.execute(
        """
        INSERT INTO users (tid, fname, lname, username, created)
        VALUES (%(tid)s, %(fname)s, %(lname)s, %(username)s, %(created)s);
        """,
        {
            "tid": user.id,
            "fname": user.first_name,
            "lname": user.last_name,
            "username": user.username,
            "created": datetime.now(timezone.utc),
        },
    )
    connection.commit()
    logging.info(f"User {user.id} has been added to the database.")
    cursor.close()
    connection.close()
    logging.debug("DB connection +")


def update_user(user: User):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE users SET fname = %(fname)s, lname = %(lname)s, username = %(username)s, created = %(created)s
        WHERE tid=%(tid)s;
        """,
        {
            "tid": user.id,
            "fname": user.first_name,
            "lname": user.last_name,
            "username": user.username,
            "created": datetime.now(timezone.utc),
        },
    )
    connection.commit()
    logging.info(f"User {user.id} info has been updated.")
    cursor.close()
    connection.close()
    logging.debug("DB connection +")


def delete_user(user: User):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE tid = %s;", (user.id,))
    connection.commit()
    logging.info(f"User {user.id} has been deleted from the database.")
    cursor.close()
    connection.close()
    logging.debug("DB connection +")