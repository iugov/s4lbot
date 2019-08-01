# -*- coding: utf-8 -*-
import commands
import logging

from telegram import MessageEntity
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from settings import API_TOKEN

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", commands.start))
    dp.add_handler(
        MessageHandler(
            Filters.text
            & (
                Filters.entity(MessageEntity.URL)
                | Filters.entity(MessageEntity.TEXT_LINK)
            ),
            commands.add_links,
        )
    )
    dp.add_handler(MessageHandler(Filters.regex("View all"), commands.get_links))
    dp.add_handler(MessageHandler(Filters.regex("Add"), commands.not_implemented))
    dp.add_handler(MessageHandler(Filters.regex("Delete"), commands.not_implemented))
    dp.add_handler(MessageHandler(Filters.regex("Help"), commands.help))
    dp.add_handler(MessageHandler(Filters.command, commands.unknown))
    dp.add_handler(MessageHandler(~Filters.command, commands.unknown))

    dp.add_error_handler(commands.error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
