# -*- coding: utf-8 -*-
from functools import wraps
import logging
import random
import sys

sys.path.append("src")

from utils import db


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Initiate | {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Finished | {func.__name__}\n\n")
        return result

    return wrapper


def get_random_id(connection):
    user_ids = [record.id for record in db.get_users(connection)]
    while True:
        tid = random.randint(100000000, 999999999)
        if tid not in user_ids:
            logging.info(f"Generated tid: {tid}")
            return tid
