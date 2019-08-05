# -*- coding: utf-8 -*-
from pathlib import Path
import requests
import bs4


PROMPTS = {
    "welcome": open(Path("src/assets/text/welcome.md"), "r").read(),
    "alpha": open(Path("src/assets/text/alpha.md"), "r").read(),
    "help": open(Path("src/assets/text/help.md"), "r").read(),
    "no_access": open(Path("src/assets/text/no_access.md"), "r").read(),
}


def get_title(url):
    """Extracts the <title> tag from url.
    Supports incomplete urls, such as 'example.com' instead of 'http://www.example.com'.
    
    Arguments:
        url {str} -- webpage url
    
    Returns:
        str -- contents of the <title> tag.
    """
    success = False
    while not success:
        try:
            response = requests.get(url)
            success = True
        except requests.exceptions.MissingSchema:
            if not url.startswith("www."):
                url = "www." + url
            if not url.startswith("http://"):
                url = "http://" + url
    page = bs4.BeautifulSoup(response.text, features="html.parser")
    return page.title.text
