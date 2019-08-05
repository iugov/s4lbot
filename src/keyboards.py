# -*- coding: utf-8 -*-
from telegram import KeyboardButton, ReplyKeyboardMarkup


def home():
    keyboard_markup = [[KeyboardButton("🗄️ View all")], [KeyboardButton("ℹ️ Help")]]
    return ReplyKeyboardMarkup(keyboard_markup, resize_keyboard=True)


# def link_overview(link):
#     keyboard_markup = [
#         [InlineKeyboardButton("Open", url=link)],
#         [InlineKeyboardButton("Edit", callback_data='edit'), InlineKeyboardButton("Delete", callback_data='delete')],
#         [InlineKeyboardButton("« Back to links", callback_data='back_to_links')]
#     ]
#     return InlineKeyboardMarkup(keyboard_markup, resize_keyboard=True)


# def link_edit(link):
#     keyboard_markup = [
#         [InlineKeyboardButton("Edit title", callback_data='edit_title'), InlineKeyboardButton("Edit url", callback_data='edit_url')],
#         [InlineKeyboardButton("« Back to the link overview", callback_data='back_to_overview')]
#     ]
#     return InlineKeyboardMarkup(keyboard_markup, resize_keyboard=True)


# def link_delete(link):
#     keyboard_markup = [
#         [InlineKeyboardButton("Yes, delete this link", callback_data='delete')],
#         [InlineKeyboardButton("« Back to to the link overview", callback_data='back_to_overview')]
#     ]
#     return InlineKeyboardMarkup(keyboard_markup, resize_keyboard=True)
