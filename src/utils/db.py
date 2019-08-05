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
    # TODO: Consider using psycopg2.extras.NamedTupleCursor instead.
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
        INSERT INTO users (tid, fname, lname, username, last_active)
        VALUES (%(tid)s, %(fname)s, %(lname)s, %(username)s, %(last_active)s);
        """,
        {
            "tid": user.id,
            "fname": user.first_name,
            "lname": user.last_name,
            "username": user.username,
            "last_active": datetime.now(timezone.utc),
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
        UPDATE users SET fname = %(fname)s, lname = %(lname)s, username = %(username)s, last_active = %(last_active)s
        WHERE tid=%(tid)s;
        """,
        {
            "tid": user.id,
            "fname": user.first_name,
            "lname": user.last_name,
            "username": user.username,
            "last_active": datetime.now(timezone.utc),
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


def add_links(links, user: User):
    if not lookup_user(user):
        logging.error(f"User {user.id} does not exist. Exiting.")
        return

    connection = connect()
    cursor = connection.cursor()

    logging.info(f"Adding '{', '.join(links)}' to the database...")

    data = [(user.id, link) for link in links]

    insert_query = "INSERT INTO userdata (tid, url) VALUES %s"

    psycopg2.extras.execute_values(
        cursor, insert_query, data, template=None, page_size=50
    )

    connection.commit()
    logging.info(
        f"Links '{', '.join(links)}' has been added to the database for User {user.id}."
    )
    cursor.close()
    close(connection)


def get_links(user: User):
    if not lookup_user(user):
        logging.warning(f"User {user.id} does not exist. Exiting.")
        return

    connection = connect()
    cursor = connection.cursor()

    logging.info(f"Retrieving links for user {user.id} ...")

    cursor.execute("SELECT * FROM userdata WHERE tid = %s;", (user.id,))

    results = cursor.fetchall()

    logging.info(f"Links retrieved from user {user.id}.")
    cursor.close()
    close(connection)

    return [record[2] for record in results]  # Return only urls.


def delete_link(link, user: User):
    if not lookup_user(user):
        logging.warning(f"User {user.id} does not exist. Exiting.")
        return

    connection = connect()
    cursor = connection.cursor()

    logging.info(f"Deleting link {link}...")

    cursor.execute(
        "DELETE FROM userdata WHERE url = %s AND tid = %s;", (link.casefold(), user.id)
    )
    connection.commit()
    logging.info(f"User {user.id} has been deleted from the database.")
    cursor.close()
    close(connection)
