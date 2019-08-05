# -*- coding: utf-8 -*-
from functools import wraps
import logging


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Initiate | {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Finished | {func.__name__}\n\n")
        return result

    return wrapper
