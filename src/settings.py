# -*- coding: utf-8 -*-
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
}

# List of developers' telegram handles.
DEVELOPERS = [334425818, 266888211]
