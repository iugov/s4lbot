# -*- coding: utf-8 -*-
"""This module contains constants and environment variables, which are required to run the bot."""

import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

# Telegram configuration.
API_TOKEN = os.getenv("API_TOKEN")

# PostgreSQL configuration.
DB = {
    "user": os.getenv("DB_USER"),
    "passwd": os.getenv("DB_PASSWD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "name": os.getenv("DB_NAME"),
    "krbsrvname": os.getenv("DB_KRBSRVNAME"),
}

# List of developers' telegram ids.
DEVELOPERS = [334425818]
