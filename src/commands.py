# -*- coding: utf-8 -*-
from utils.text_processing import extract_urls, fetch_text
from pathlib import Path
from settings import DEVELOPERS
import telegram
import requests
import re


def authorize_developer(func):
    def command(bot, update):
        if update.message.from_user.username not in DEVELOPERS:
            bot.send_message(
                chat_id=update.message.chat_id,
                text=fetch_text(Path("src/assets/text/no_access.txt")),
            )
            return

    return command


def get_url():
    contents = requests.get("https://random.dog/woof.json").json()
    url = contents["url"]
    return url


def send_content(bot, chat_id, content):
    image_extensions = ["jpg", "jpeg", "png"]
    video_extensions = ["mp4", "mov", "webm"]
    animation_extensions = ["gif"]

    allowed_extensions = image_extensions + video_extensions + animation_extensions

    file_extension = ""
    while file_extension not in allowed_extensions:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()

    if file_extension in image_extensions:
        bot.send_photo(chat_id=chat_id, photo=url)

    if file_extension in video_extensions:
        bot.send_video(chat_id=chat_id, video=url)

    if file_extension in animation_extensions:
        bot.send_animation(chat_id=chat_id, animation=url)


@authorize_developer
def info(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=fetch_text(Path("src/assets/text/credits.txt")),
    )


@authorize_developer
def start(bot, update):

    kb = [
        [telegram.InlineKeyboardButton("NEXT DOGGO"), telegram.KeyboardButton("INFO")]
    ]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, resize_keyboard=True)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=fetch_text(Path("src/assets/text/start.txt")),
        reply_markup=kb_markup,
    )
    bot.send_photo(chat_id=update.message.chat_id, photo=get_url())


@authorize_developer
def unknown(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id, text="Hmm... I don't know that one."
    )


@authorize_developer
def next_dog(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    send_content(bot=bot, chat_id=chat_id, content=url)


@authorize_developer
def echo_urls(bot, update):
    urls = extract_urls(update.message.text)
    if urls:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Link(s) found: {}.".format(", ".join(urls)),
        )
