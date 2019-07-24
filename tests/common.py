# -*- coding: utf-8 -*-
import logging
import sys
from functools import wraps

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Initiate | {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Finished | {func.__name__}\n\n")
        return result

    return wrapper
