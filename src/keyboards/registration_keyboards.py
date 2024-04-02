from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_location_keyboard_markup():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(
        text='Отправить геолокацию',
        request_location=True
    ))
    return builder.as_markup(resize_keyboard=True)


skip_add_cities_texts = ['Прекратить ввод городов']

skip_add_links_texts = ['Прекратить ввод ссылок']


def get_skip_add_cities_markup():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(
        text=skip_add_cities_texts[0],
    ))
    return builder.as_markup(resize_keyboard=True)


def get_skip_add_links_markup():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(
        text=skip_add_links_texts[0],
    ))
    return builder.as_markup(resize_keyboard=True)


def get_fuzz_variants_markup():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Принять', callback_data='apply'),
        types.InlineKeyboardButton(
            text='Отказаться', callback_data='deny'
        )
    )
    return builder.as_markup(resize_keyboard=True)
