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
        results = cursor.fetchone()

    if results:
        logging.info(f"Found user {uid}.")
    else:
        logging.info(f"User not found.")

    return results


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


def update_user(connection, new_user: User, old_user):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Updating user {new_user.id}...")

        cursor.execute(
            """
            UPDATE users SET first_name = %(first_name)s WHERE id = %(id)s;
            """,
            {"id": old_user.id, "first_name": new_user.first_name},
        )

    logging.info(f"User {new_user.id} has been added to the database.")


def delete_user(connection, user: User):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Deleting user {user.id}...")
        cursor.execute("DELETE FROM users WHERE id = %s;", (user.id,))

    logging.info(f"User {user.id} has been deleted from the database.")


def add_links(connection, links, user: User):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        if not lookup_user(connection, user.id):
            logging.error(f"User {user.id} does not exist.")
            return

        logging.info(f"Adding '{', '.join(links)}' to the database...")

        data = [(user.id, link, get_title(link)) for link in links]

        insert_query = "INSERT INTO urls (owner, url, title) VALUES %s"

        psycopg2.extras.execute_values(
            cursor, insert_query, data, template=None, page_size=50
        )

    logging.info(
        f"Links '{', '.join(links)}' has been added to the database for User {user.id}."
    )


def get_links(connection, user: User):
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        if not lookup_user(connection, user.id):
            logging.warning(f"User {user.id} does not exist. Exiting.")
            return

        logging.info(f"Retrieving links for user {user.id} ...")

        cursor.execute("SELECT * FROM urls WHERE owner = %s;", (user.id,))

        results = cursor.fetchall()

    logging.info(f"Links retrieved from user {user.id}.")
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
