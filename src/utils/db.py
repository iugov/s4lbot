# -*- coding: utf-8 -*-
import logging
import sys

import psycopg2
import psycopg2.extras

from settings import DB

sys.path.append("src")


def connect():
    connection = psycopg2.connect(
        user=DB["user"],
        password=DB["passwd"],
        host=DB["host"],
        port=DB["port"],
        database=DB["name"],
    )

    logging.info("Database connection established successfully.")
    logging.info(connection.get_dsn_parameters())

    return connection


def lookup_user(tid):
    connection = connect()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM users WHERE tid=%s", (tid,))
    results = cursor.fetchone()

    cursor.close()
    connection.close()

    return results


def add_user(update):
    user = update.message.from_user

    connection = connect()
    cursor = connection.cursor()
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
            "created": update.message.date,
        },
    )
    connection.commit()
    cursor.close()
    connection.close()


def update_user(update):
    user = update.message.from_user

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
            "created": update.message.date,
        },
    )
    connection.commit()
    cursor.close()
    connection.close()
