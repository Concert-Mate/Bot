from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def create_resizable_inline_keyboard(builder: InlineKeyboardBuilder) -> InlineKeyboardMarkup:
    return builder.as_markup(resize_keyboard=True)


def create_resizable_reply_keyboard(builder: ReplyKeyboardBuilder) -> ReplyKeyboardMarkup:
    return builder.as_markup(resize_keyboard=True)
