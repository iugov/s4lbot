from settings import API_TOKEN

from telegram.ext import Updater, InlineQueryHandler, CommandHandler, RegexHandler
import telegram
import requests
import time
import re

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def get_url():
    contents = requests.get("https://random.dog/woof.json").json()
    url = contents["url"]
    return url


def next_dog(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def info(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="S4L bot is under development.\n\nAuthor: @antoniugov",
    )


def start(bot, update):
    kb = [
        [telegram.InlineKeyboardButton("NEXT DOGGO"), telegram.KeyboardButton("INFO")]
    ]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, resize_keyboard=True)

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hi! This bot is currently under development.\n\nMeanwhile, enjoy an endless supply of these magnificent creatures.",
        reply_markup=kb_markup,
    )
    bot.send_photo(chat_id=update.message.chat_id, photo=get_url())


def main():
    updater = Updater(API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(RegexHandler("NEXT DOGGO", next_dog))
    dp.add_handler(RegexHandler("INFO", info))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
