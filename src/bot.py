# -*- coding: utf-8 -*-
"""This module contains the entry point of the bot and it's configuration instructions."""

import logging

from telegram import MessageEntity
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

import callbacks
from settings import API_TOKEN

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", callbacks.start))

    # Handles messages with valid urls.
    dp.add_handler(
        MessageHandler(
            Filters.text
            & (
                Filters.entity(MessageEntity.URL)
                | Filters.entity(MessageEntity.TEXT_LINK)
            ),
            callbacks.add_links,
        )
    )
    dp.add_handler(MessageHandler(Filters.regex("View all"), callbacks.get_links))
    dp.add_handler(CommandHandler("all", callbacks.get_links))

    dp.add_handler(MessageHandler(Filters.regex("Help"), callbacks.help))
    dp.add_handler(CommandHandler("help", callbacks.help))

    # Enter 'link_expand' menu (see `src/keyboards.py`).
    dp.add_handler(CallbackQueryHandler(callbacks.expand_link, pattern="expand"))

    # Enter 'link_delete' menu (see `src/keyboards.py`).
    dp.add_handler(CallbackQueryHandler(callbacks.delete_link, pattern="delete"))

    # Delete link when deletion is confirmed.
    dp.add_handler(
        CallbackQueryHandler(callbacks.delete_link_confirmed, pattern="confirm_delete")
    )

    # Return to the previous inline menu (specified ReplyMarkup, effectively).
    dp.add_handler(CallbackQueryHandler(callbacks.go_back, pattern="back_to"))

    dp.add_handler(MessageHandler(Filters.command, callbacks.unknown))

    dp.add_error_handler(callbacks.error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
