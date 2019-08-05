# -*- coding: utf-8 -*-
import logging
from functools import wraps

import telegram
from telegram import Update
from telegram.ext import CallbackContext

import keyboards
from settings import DEVELOPERS
from utils import db
from utils.misc import PROMPTS, get_title


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id in DEVELOPERS:
            return func(update, context, *args, **kwargs)
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=PROMPTS["no_access"],
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            return

    return wrapped


def send_typing_action(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return wrapped


@restricted
def start(update: Update, context: CallbackContext):
    user = update.message.from_user

    if db.lookup_user(user.id):
        db.update_user(user)
    else:
        db.add_user(user)

    context.bot.send_photo(chat_id=update.message.chat_id, photo=PROMPTS["img_cover"])

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=PROMPTS["start"],
        reply_markup=keyboards.home(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def help(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=PROMPTS["help"].format(all="/all".center(6), help="/help".center(7)),
        reply_markup=telegram.InlineKeyboardMarkup(
            [
                [
                    telegram.InlineKeyboardButton(
                        "Contribute on GitHub!", url="https://github.com/iugov/s4lbot"
                    )
                ]
            ]
        ),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Hmm... I don't know that one. Have you tried */help*?",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


@send_typing_action
def add_links(update: Update, context: CallbackContext):
    urls = update.message.parse_entities(["url", "text_link"]).values()

    if urls:
        logging.info(f"Got content of type url, text_link: {urls}")

        distinct_links = set([url.casefold() for url in urls]) - set(
            db.get_links(update.message.from_user)
        )
        if distinct_links:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"⏳ Saving your link{'s' if len(distinct_links) > 1 else ''}... ⏳",
                disable_notification=True,
            )
            db.add_links(distinct_links, update.message.from_user)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"✨ {len(distinct_links)} link{'s' if len(distinct_links) > 1 else ''} saved. ✨",
                disable_notification=True,
            )
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"You already have that link saved! You can find it with 'View all'.",
            )


@send_typing_action
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
            text="You don't have any saved links. To save one, simply type/forward it here!",
        )
        return False

    button_list = [
        telegram.InlineKeyboardButton(get_title(link), url=link) for link in links
    ]

    reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Here are your links.",
        reply_markup=reply_markup,
    )
