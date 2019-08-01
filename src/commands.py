# -*- coding: utf-8 -*-
import logging
from pathlib import Path

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
            return func(update, context)
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=from_file(Path("src/assets/text/no_access.txt")),
            )

    return command


@developers_only
def start(update: Update, context: CallbackContext):
    user = update.message.from_user

    if db.lookup_user(user.id):
        db.update_user(user)
    else:
        db.add_user(user)

    kb_markup = telegram.ReplyKeyboardMarkup(keyboards.HOME, resize_keyboard=True)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/start.txt")),
        reply_markup=kb_markup,
    )


def help(update: Update, context: CallbackContext):
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


def not_implemented(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=from_file(Path("src/assets/text/not_implemented.txt")),
    )


def error(update: Update, context: CallbackContext):
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
