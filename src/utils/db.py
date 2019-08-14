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
    """Connect to the database.

        Returns:
            :class:`psycopg2.extensions.connection`: On success, connection object is returned.
    """

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
    """Fetch user from the database.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.
            uid (:obj:`int`): User's id (unique identifier provided by Telegram).

        Returns:
            :class:`psycopg2.extras.Record`: On success, user record (named tuple) is returned.
    """
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
    """Fetch all users from the database.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.

        Returns:
            List[:class:`psycopg2.extras.Record`]: On success, list of user records (named tuples) is returned.
    """
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Fetching all users...")

        cursor.execute("SELECT * FROM users;")

        users = cursor.fetchall()

    return users


def add_user(connection, user: User, timestamp):
    """Add user to the database.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.
            user: (:class:`telegram.user.User`): User object.
            timestamp (:obj:`datetime.datetime`): Datetime object.
    """
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
    """Update info for an existing user.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.
            new_user: (:class:`telegram.user.User`): User object.
            old_user: (:class:`telegram.user.User`): User object.
    """
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
    """Delete an existing user.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.
            user: (:class:`telegram.user.User`): User object.
    """
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Deleting user {user.id}...")
        cursor.execute("DELETE FROM users WHERE id = %s;", (user.id,))

    logging.info(f"User {user.id} has been deleted from the database.")


def add_links(connection, links, user: User):
    """Insert a number of links into the 'urls' table.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.
            links: (List[:obj:`str`]): List of raw urls.
            user: (:class:`telegram.user.User`): User object.
    """
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
    """Retrieve all links from the 'urls' table for the specified user.
        
        Args:
            connection (:class:`psycopg2.extensions.connection`): Connection object.
            user: (:class:`telegram.user.User`): User object.
        
        Returns:
            List[:class:`psycopg2.extras.Record`]: On success, list of links (named tuples) is returned.
    """
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
    """Retrieve a link from 'urls' table based on it's unique id.
        
        Args:
            link_id: (:obj:`int`): Link's id.
        
        Returns:
            :class:`psycopg2.extras.Record`: On success, one link (named tuple) is returned.
    """
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s;", (link_id,))
        result = cursor.fetchone()

    return result


def delete_link(connection, link_id):
    """Delete a link from 'urls' table based on it's unique id.
        
        Args:
            link_id: (:obj:`int`): Link's id.
    """
    with connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        logging.info(f"Deleting link {link_id}...")
        cursor.execute("DELETE FROM urls WHERE id = %s;", (link_id,))

    logging.info(f"Link {link_id} has been deleted from the database.")
