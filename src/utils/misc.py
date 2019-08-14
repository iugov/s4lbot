# -*- coding: utf-8 -*-
from pathlib import Path
import requests
import bs4


# 'welcome': Welcome message. Used when `/start` command is invoked.
# 'alpha': Alpha version notice.
# Used when `/start` command is invoked in a development version of the bot.
# 'help': Help message. Used when `/help` command is invoked.
PROMPTS = {
    "welcome": open(Path("src/assets/text/welcome.md"), "r").read(),
    "alpha": open(Path("src/assets/text/alpha.md"), "r").read(),
    "help": open(Path("src/assets/text/help.md"), "r").read(),
}


def get_title(url):
    """Extracts the <title> tag from url.
    Supports incomplete urls, such as 'example.com' instead of 'http://www.example.com'.
    
    Args:
        url (:obj:`str`): URL.
    
    Returns:
        :obj:`str`: Contents of the <title> tag.
    """
    original_url = url
    success = False
    while not success:
        try:
            response = requests.get(url)
            success = True
        except requests.exceptions.MissingSchema:
            url = "http://" + url
        except requests.exceptions.RequestException:  # If something goes horribly wrong, return url as title
            return original_url

    page = bs4.BeautifulSoup(response.text, features="html.parser")

    try:
        title = page.title.text
    except AttributeError:
        return original_url

    return title
