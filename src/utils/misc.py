# -*- coding: utf-8 -*-
from pathlib import Path
from lxml.html import fromstring
import requests


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
    """Extracts the contents of <title> tag from url.
    
    Args:
        url (:obj:`str`): URL.
    
    Returns:
        :obj:`str`: Contents of the <title> tag.
    """
    try:
        response = requests.get(url, headers={"Accept-Language": "en-US,en;q=0.5"})
    except requests.exceptions.RequestException:
        return url

    title = fromstring(response.content).findtext(".//title")

    return title if title else url
