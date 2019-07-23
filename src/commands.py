# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path

import requests
import telegram

from settings import DEVELOPERS
from utils import db
from utils.text_processing import from_file
from telegram import Update
from telegram.ext import CallbackContext


def developers_only(func):
    def command(update: Update, context: CallbackContext):
        if update.message.from_user.id in DEVELOPERS:
            func(update, context)
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=from_file(Path("src/assets/text/no_access.txt")),
            )

    return command


@developers_only
def start(update: Update, context: CallbackContext):

    # TODO: Clean this shit up and make separate functions and modules.
    user = update.message.from_user
    record = db.lookup_user(user.id)

    if record:
        msg = f"Yay! You are already in the database, {user.first_name}."
        msg += f'\n\nYour unique telegram id is: {record["tid"]}'
        msg += f'\n\nYour username is: {record["username"]}'
        msg += f'\n\nYou last used /start command at: {record["created"].strftime("%b %d %Y, %H:%M:%S")}'
        db.update_user(user)
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Hi, {user.first_name}!\n\nYou are new.\n\nAdding to database...",
        )
        db.add_user(user)
        msg = f"Done! Enjoy your stay.\n\nTo view your data, invoke /start ;)"

    context.bot.send_message(chat_id=update.message.chat_id, text=msg)

    kb = [
        [telegram.InlineKeyboardButton("NEXT DOGGO"), telegram.KeyboardButton("INFO")]
    ]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, resize_keyboard=True)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/start.txt")),
        reply_markup=kb_markup,
    )

    next_dog(update, context)


def info(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/credits.txt")),
    )


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/unknown.txt")),
    )


def find_links(update: Update, context: CallbackContext):
    urls = update.message.parse_entities(["url", "text_link"])
    logging.info(f"Got entities: {urls}")
    if urls:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Link(s) found: {}.".format(", ".join(urls.values())),
        )


def next_dog(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    image_extensions = ["jpg", "jpeg", "png"]
    video_extensions = ["mp4", "mov", "webm"]
    animation_extensions = ["gif"]

    allowed_extensions = image_extensions + video_extensions + animation_extensions

    file_extension = ""
    while file_extension not in allowed_extensions:
        url = requests.get("https://random.dog/woof.json").json()["url"]
        file_extension = re.search("([^.]*)$", url).group(1).lower()

    if file_extension in image_extensions:
        context.bot.send_photo(chat_id=chat_id, photo=url)

    if file_extension in video_extensions:
        context.bot.send_video(chat_id=chat_id, video=url)

    if file_extension in animation_extensions:
        context.bot.send_animation(chat_id=chat_id, animation=url)
