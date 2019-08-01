# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path

import requests
import telegram
import keyboards

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

    # TODO: Remove the test code.
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
    kb_markup = telegram.ReplyKeyboardMarkup(keyboards.HOME, resize_keyboard=True)

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
        reply_markup=telegram.InlineKeyboardMarkup(
            [
                [
                    telegram.InlineKeyboardButton(
                        "Contribute on GitHub!", url="https://github.com/iugov/s4lbot"
                    )
                ]
            ]
        ),
    )


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/unknown.txt")),
    )


def not_implemented(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/not_implemented.txt")),
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def add_links(update: Update, context: CallbackContext):
    urls = update.message.parse_entities(["url", "text_link"]).values()

    if urls:
        logging.info(f"Got urls: {urls}")

        distinct_links = set([url.casefold() for url in urls]) - set(
            db.get_links(update.message.from_user)
        )
        db.add_links(distinct_links, update.message.from_user)
        if distinct_links:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"{len(distinct_links)} link{'s' if len(distinct_links) > 1 else ''} saved.",
            )


def get_links(update: Update, context: CallbackContext):
    def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
        menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu

    links = db.get_links(update.message.from_user)

    if not links:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="You don't have any saved links. To save one, simply forward it here!",
        )
        return False

    button_list = [telegram.InlineKeyboardButton(link, url=link) for link in links]

    reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Here are your links.",
        reply_markup=reply_markup,
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
