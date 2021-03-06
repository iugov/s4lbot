# -*- coding: utf-8 -*-
"""This module contains functions, which are used in Handlers provided by the 'python-telegram-bot' package."""

import logging
from functools import wraps

import telegram
from telegram import Update
from telegram.ext import CallbackContext

import keyboards
from utils import db
from utils.misc import PROMPTS


def send_typing_action(func):
    """Display `typing` in chat when executing a callback function."""

    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return wrapped


def start(update: Update, context: CallbackContext):
    """Called on `/start`. Add/update user and introduce them to the bot."""
    user = update.message.from_user

    with db.connect() as connection:
        user = db.lookup_user(connection, update.message.from_user.id)
        if not user:
            db.add_user(
                connection,
                update.message.from_user,
                timestamp=update.effective_message.date,
            )
        elif user.first_name != update.message.from_user.first_name:
            db.update_user(connection, update.message.from_user, user.id)

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo="https://github.com/iugov/s4lbot/blob/develop/images/cover.jpg?raw=true",
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="{}\n\n{}".format(PROMPTS["welcome"], PROMPTS["alpha"]),
        reply_markup=keyboards.home(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def help(update: Update, context: CallbackContext):
    """Called on `/help`. Displays a help message."""
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=PROMPTS["help"],
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
    """Called whenever an unrecognized command is invoked."""
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="I don't know that one. Maybe try /help?",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


@send_typing_action
def add_links(update: Update, context: CallbackContext):
    """Parse urls from message, add all unique new ones to the database."""
    urls = update.message.parse_entities(["url", "text_link"]).values()

    if urls:
        logging.info(f"Got content of type url, text_link: {urls}")

        with db.connect() as connection:
            existing_links = db.get_links(connection, update.message.from_user.id)
            if existing_links:
                distinct_links = set([url.casefold() for url in urls]) - set(
                    [link.url for link in existing_links]
                )
            else:
                distinct_links = set([url.casefold() for url in urls])

            if distinct_links:
                success = context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=f"⏳ Saving your link{'s' if len(distinct_links) > 1 else ''}... ⏳",
                    disable_notification=True,
                )

                db.add_links(connection, distinct_links, update.message.from_user.id)

                context.bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    message_id=success.message_id,
                    text=f"✨ {len(distinct_links)} link{'s' if len(distinct_links) > 1 else ''} saved ✨",
                )
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=f"You already have that link saved! Look it up with *View all* or */all*",
                    parse_mode=telegram.ParseMode.MARKDOWN,
                )


@send_typing_action
def get_links(update: Update, context: CallbackContext, editable_message_id=None):
    """Display an inline menu with user's links.
        
        Args:
            update (:class:`telegram.Update`): Update object.
            update (:class:`telegram.CallbackContext`): CallbackContext object.
            editable_message_id (:obj:`int`): Id of the message to be edited (this is used to invoke this
            function from within CallbackQueryHandler's callback function and be able to edit the original keyboard)
    """

    def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
        menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu

    with db.connect() as connection:
        links = db.get_links(connection, update.effective_user.id)

        if not links:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"You don't have any saved links.",
            )
            return

        buttons = []
        for link in links:
            buttons.append(
                telegram.InlineKeyboardButton(
                    link.title, callback_data=f"expand:{link.id}"
                )
            )

    reply_markup = telegram.InlineKeyboardMarkup(build_menu(buttons, n_cols=1))

    if editable_message_id:
        return context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=editable_message_id,
            text=f"Other links you saved:",
            reply_markup=reply_markup,
        )
    else:
        return context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"You saved:",
            reply_markup=reply_markup,
        )


def expand_link(update: Update, context: CallbackContext):
    """Display an inline menu with user's links.
    
    CallbackQuery.data holds a string with the following syntax: "expand:{LINK_ID}".
    We use that LINK_ID to fetch the link from the database and show it via `link_expand` keyboard.

        Args:
            update (:class:`telegram.Update`): Update object.
            update (:class:`telegram.CallbackContext`): CallbackContext object.
    """
    query = update.callback_query
    link_id = query.data.split("expand:")[1]

    with db.connect() as connection:
        link = db.get_link(connection, link_id)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"Here it is: {link.title}",
        reply_markup=keyboards.link_expand(link),
    )

    query.answer()


def delete_link(update: Update, context: CallbackContext):
    """Display an inline menu with a confirmation prompt.
    
    CallbackQuery.data holds a string with the following syntax: "delete:{LINK_ID}".
    We use that LINK_ID to fetch the link from the database and show it via `link_delete` keyboard.

        Args:
            update (:class:`telegram.Update`): Update object.
            update (:class:`telegram.CallbackContext`): CallbackContext object.
    """
    query = update.callback_query
    link_id = query.data.split("delete:")[1]

    with db.connect() as connection:
        link = db.get_link(connection, link_id)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f'You are about to delete a link to "{link.title}" ({link.url})\nAre you sure?',
        reply_markup=keyboards.link_delete(link),
    )

    query.answer()


def delete_link_confirmed(update: Update, context: CallbackContext):
    """Delete the link specified in the callback query.
    
    CallbackQuery.data holds a string with the following syntax: "confirm_delete:{LINK_ID}".
    We use that LINK_ID to delete that link from the database.

        Args:
            update (:class:`telegram.Update`): Update object.
            update (:class:`telegram.CallbackContext`): CallbackContext object.
    """
    query = update.callback_query
    link_id = query.data.split("confirm_delete:")[1]

    with db.connect() as connection:
        link = db.get_link(connection, link_id)
        db.delete_link(connection, link_id)

        msg = context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=f'"{link.title}" link has been deleted.',
        )

    get_links(update, context, editable_message_id=msg.message_id)


def go_back(update: Update, context: CallbackContext):
    """Return to the inline menu specified in the callback query.
    
    CallbackQuery.data holds a string with the following syntax: "back_to:[links|expand:{LINK_ID}]".
      - `links` token suggests that we should return to an overview of all links (by calling get_links).
      - `expand` token suggests that we should return to a particular link overview (also specified in the token)

        Args:
            update (:class:`telegram.Update`): Update object.
            update (:class:`telegram.CallbackContext`): CallbackContext object.
    """
    query = update.callback_query
    query.answer()

    choice = query.data.split("back_to:")[1]

    if "links" in choice:
        get_links(update, context, editable_message_id=query.message.message_id)
    elif "expand" in choice:
        expand_link(update, context)
