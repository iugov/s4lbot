from telegram.ext import Updater, CommandHandler, RegexHandler, MessageHandler, Filters

import commands
import settings
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    updater = Updater(settings.API_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", commands.start))
    dp.add_handler(CommandHandler("links", commands.echo_urls))

    dp.add_handler(RegexHandler("NEXT DOGGO", commands.next_dog))
    dp.add_handler(RegexHandler("INFO", commands.info))

    dp.add_handler(MessageHandler(Filters.command, commands.unknown))
    dp.add_handler(MessageHandler(~Filters.command, commands.unknown))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
