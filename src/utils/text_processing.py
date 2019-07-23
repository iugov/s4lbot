# -*- coding: utf-8 -*-
def from_file(path):
    try:
        with open(path, "r") as f:
            contents = f.read()
    except IOError:
        contents = "Sadly, an error occured. Try again later."
        pass
    return contents
