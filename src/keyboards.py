# -*- coding: utf-8 -*-
from telegram import (
    KeyboardButton,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
)


def home():
    keyboard_markup = [[KeyboardButton("🗄️ View all"), KeyboardButton("ℹ️ Help")]]
    return ReplyKeyboardMarkup(keyboard_markup, resize_keyboard=True)


def link_expand(link):
    keyboard_markup = [
        [InlineKeyboardButton("Open", url=link.url)],
        [InlineKeyboardButton("Delete", callback_data=f"delete:{link.id}")],
        [InlineKeyboardButton("« Back to links", callback_data="back_to:links")],
    ]
    return InlineKeyboardMarkup(keyboard_markup, resize_keyboard=True)


def link_delete(link):
    keyboard_markup = [
        [
            InlineKeyboardButton(
                "Yes, I'm sure", callback_data=f"confirm_delete:{link.id}"
            )
        ],
        [
            InlineKeyboardButton(
                "« Back to to link overview", callback_data=f"back_to:expand:{link.id}"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard_markup, resize_keyboard=True)
