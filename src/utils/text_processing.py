# -*- coding: utf-8 -*-
from urlextract import URLExtract


def extract_urls(text):
    return URLExtract().find_urls(text)


def fetch_text(path):
    try:
        with open(path, "r") as f:
            contents = f.read()
    except IOError:
        contents = "Sadly, an error occured. Try again later."
        pass
    return contents
