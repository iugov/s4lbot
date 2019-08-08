# -*- coding: utf-8 -*-
import callbacks
import logging

from telegram import MessageEntity
from telegram.ext import (
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    CallbackQueryHandler,
)

from settings import API_TOKEN

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", callbacks.start))
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

    dp.add_handler(
        CallbackQueryHandler(callbacks.expand_link, pattern="expand")
    )  # Enter link overview menu.
    dp.add_handler(
        CallbackQueryHandler(callbacks.delete_link, pattern="delete")
    )  # Enter link deletion menu.
    dp.add_handler(
        CallbackQueryHandler(callbacks.delete_link_confirmed, pattern="confirm_delete")
    )

    dp.add_handler(CallbackQueryHandler(callbacks.go_back, pattern="back_to"))

    dp.add_handler(MessageHandler(Filters.command, callbacks.unknown))

    dp.add_error_handler(callbacks.error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
