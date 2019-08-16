# -*- coding: utf-8 -*-
"""This module contains miscellaneous functions and variables used by the bot."""

from pathlib import Path

import requests
from lxml.html import fromstring  # nosec


# 'welcome': Welcome message. Used when `/start` command is invoked.
# 'alpha': Alpha version notice.
# Used when `/start` command is invoked in a development version of the bot.
# 'help': Help message. Used when `/help` command is invoked.
PROMPTS = {
    "welcome": open(Path("src/assets/text/welcome.md"), "r").read(),
    "alpha": open(Path("src/assets/text/alpha.md"), "r").read(),
    "help": open(Path("src/assets/text/help.md"), "r").read(),
}


def get_title(url, lang="en"):
    """Extracts the contents of <title> tag from url.

    Args:
        url (:obj:`str`): URL.

    Returns:
        :obj:`str`: Contents of the <title> tag.
    """
    lang_header = {"en": "en-US, en", "ru": "ru-RU, ru"}

    try:
        response = requests.get(url, headers={"Accept-Language": lang_header[lang]})
    except requests.exceptions.RequestException:
        return url

    title = fromstring(response.content).findtext(".//title")  # nosec

    return title if title else url
