# -*- coding: utf-8 -*-
import commands
import logging

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
            Filters.text & (Filters.entity("url") | Filters.entity("text_link")),
            commands.find_links,
        )
    )
    dp.add_handler(MessageHandler(Filters.regex("NEXT DOGGO"), commands.next_dog))
    dp.add_handler(MessageHandler(Filters.regex("INFO"), commands.info))
    dp.add_handler(MessageHandler(Filters.command, commands.unknown))
    dp.add_handler(MessageHandler(~Filters.command, commands.unknown))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
