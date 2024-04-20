from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Изменить данные', callback_data='change_data'),
        types.InlineKeyboardButton(
            text='Инструменты', callback_data='tools'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Информация о пользователе', callback_data='user_info'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='F.A.Q', callback_data='FAQ'),
    )

    return builder.as_markup(resize_keyboard=True)


def get_change_data_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Добавить город', callback_data='add_city'),
        types.InlineKeyboardButton(
            text='Удалить город', callback_data='remove_city'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Добавить плейлист', callback_data='add_playlist'),
        types.InlineKeyboardButton(
            text='Удалить плейлист', callback_data='remove_playlist'),
    )

    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data='back'),
    )

    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Отменить', callback_data='cancel'),
    )

    return builder.as_markup(resize_keyboard=True)


def create_inline_keyboard_with_back(rows: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for row in rows:
        builder.row(
            types.InlineKeyboardButton(
                text=row, callback_data=row),
        )
    builder.row(types.InlineKeyboardButton(
        text='Назад', callback_data='back',
    ))

    return builder.as_markup(resize_keyboard=True)


def get_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Что умеет этот бот', callback_data='main_info'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Связь с разработчиком', callback_data='dev_comm'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data='back'),
    )

    return builder.as_markup(resize_keyboard=True)


def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data='back'),
    )

    return builder.as_markup(resize_keyboard=True)


def get_user_info_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Города', callback_data='cities'),
        types.InlineKeyboardButton(
            text='Плейлисты', callback_data='links'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data='back'),
    )

    return builder.as_markup(resize_keyboard=True)


def get_tools_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Показать возможные концерты', callback_data='show_concerts'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Показ уведомлений', callback_data='notice_management'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data='back'),
    )

    return builder.as_markup(resize_keyboard=True)


def get_notify_management_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_enabled:
        builder.row(
            types.InlineKeyboardButton(
                text='Отключить', callback_data='disable'),
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text='Включить', callback_data='enable'),
        )

    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data='back'),
    )

    return builder.as_markup(resize_keyboard=True)
