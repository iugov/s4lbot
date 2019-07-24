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
    logging.debug(f"DB pid-{connection.get_backend_pid()} [ OPEN ]")
    return connection


def close(connection):
    pid = connection.get_backend_pid()
    connection.close()
    logging.debug(f"DB pid-{pid} [CLOSED]")


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
    close(connection)

    return results


def add_user(user: User):
    connection = connect()
    cursor = connection.cursor()

    logging.info(f"Adding user {user.id} to the database...")

    # FIXME: This can be simplified.
    if lookup_user(user):
        logging.warning(f"User {user.id} already exists. Returning.")
        cursor.close()
        close(connection)
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
    close(connection)


def update_user(user: User):
    connection = connect()
    cursor = connection.cursor()

    logging.info(f"Updating user {user.id}...")

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
    close(connection)


def delete_user(user: User):
    connection = connect()
    cursor = connection.cursor()

    logging.info(f"Deleting user {user.id}...")

    cursor.execute("DELETE FROM users WHERE tid = %s;", (user.id,))
    connection.commit()
    logging.info(f"User {user.id} has been deleted from the database.")
    cursor.close()
    close(connection)
