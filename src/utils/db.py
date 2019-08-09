# -*- coding: utf-8 -*-
import logging
import sys

import psycopg2
import psycopg2.extras

sys.path.append("src")

from utils.misc import get_title
from settings import DB
from telegram import User


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


def lookup_user(connection, uid):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Looking for user {uid} ...")

        cursor.execute("SELECT * FROM users WHERE id=%s", (uid,))
        user = cursor.fetchone()

    if user:
        logging.info(f"Found user {uid}.")
    else:
        logging.info(f"User not found.")

    return user


def get_users(connection):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Fetching all users...")

        cursor.execute("SELECT * FROM users;")

        users = cursor.fetchall()

    return users


def add_user(connection, user: User, timestamp):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Adding user {user.id} to the database...")

        if lookup_user(connection, user.id):
            logging.warning(f"User {user.id} already exists. Returning.")
            return

        cursor.execute(
            """
            INSERT INTO users VALUES (%(id)s, %(first_name)s, %(joined_on)s);
            """,
            {"id": user.id, "first_name": user.first_name, "joined_on": timestamp},
        )

    logging.info(f"User {user.id} has been added to the database.")


# TODO: Return user


def update_user(connection, new_user: User, uid):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Updating user {new_user.id}...")

        cursor.execute(
            """
            UPDATE users SET first_name = %(first_name)s WHERE id = %(id)s;
            """,
            {"id": uid, "first_name": new_user.first_name},
        )

    logging.info(f"User {new_user.id} has been added to the database.")


def delete_user(connection, uid):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Deleting user {uid}...")
        cursor.execute("DELETE FROM users WHERE id = %s;", (uid,))

    logging.info(f"User {uid} has been deleted from the database.")


def add_links(connection, links, uid):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        if not lookup_user(connection, uid):
            logging.error(f"User {uid} does not exist.")
            return

        logging.info(f"Adding '{', '.join(links)}' to the database...")

        data = [(uid, link, get_title(link)) for link in links]

        insert_query = "INSERT INTO urls (owner, url, title) VALUES %s"

        psycopg2.extras.execute_values(
            cursor, insert_query, data, template=None, page_size=50
        )

    logging.info(
        f"Links '{', '.join(links)}' has been added to the database for User {uid}."
    )


def get_links(connection, uid):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        if not lookup_user(connection, uid):
            logging.warning(f"User {uid} does not exist. Exiting.")
            return

        logging.info(f"Retrieving links for user {uid} ...")

        cursor.execute("SELECT * FROM urls WHERE owner = %s;", (uid,))

        results = cursor.fetchall()

    logging.info(f"Links retrieved from user {uid}.")
    return results


def get_link(connection, link_id):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s;", (link_id,))
        result = cursor.fetchone()

    return result


def delete_link(connection, link_id):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Deleting link {link_id}...")
        cursor.execute("DELETE FROM urls WHERE id = %s;", (link_id,))

    logging.info(f"Link {link_id} has been deleted from the database.")
