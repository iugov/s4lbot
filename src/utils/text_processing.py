# -*- coding: utf-8 -*-
def fetch_text(path):
    try:
        with open(path, "r") as f:
            contents = f.read()
    except IOError:
        contents = "Sadly, an error occured. Try again later."
        pass
    return contents
