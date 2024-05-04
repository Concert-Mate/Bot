from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from model.playlist import Playlist
from .callback_data import KeyboardCallbackData
from .utils import create_resizable_inline_keyboard


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Изменить данные', callback_data=KeyboardCallbackData.CHANGE_DATA),
        types.InlineKeyboardButton(
            text='Инструменты', callback_data=KeyboardCallbackData.TOOLS),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Информация о пользователе', callback_data=KeyboardCallbackData.USER_INFO),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='F.A.Q', callback_data=KeyboardCallbackData.FAQ),
    )

    return create_resizable_inline_keyboard(builder)


def get_change_data_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Добавить город', callback_data=KeyboardCallbackData.ADD_CITY),
        types.InlineKeyboardButton(
            text='Удалить город', callback_data=KeyboardCallbackData.REMOVE_CITY),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Добавить трек-лист', callback_data=KeyboardCallbackData.ADD_LINK),
        types.InlineKeyboardButton(
            text='Удалить трек-лист', callback_data=KeyboardCallbackData.REMOVE_LINK),
    )

    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data=KeyboardCallbackData.BACK),
    )

    return create_resizable_inline_keyboard(builder)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Отменить', callback_data=KeyboardCallbackData.CANCEL),
    )

    return create_resizable_inline_keyboard(builder)


def get_inline_keyboard_with_back(rows: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for row in rows:
        builder.row(
            types.InlineKeyboardButton(
                text=row, callback_data=row),
        )
    builder.row(types.InlineKeyboardButton(
        text='Назад', callback_data=KeyboardCallbackData.BACK,
    ))

    return create_resizable_inline_keyboard(builder)


def get_inline_keyboard_for_playlists(rows: list[Playlist]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for pos, row in enumerate(rows):
        builder.row(
            types.InlineKeyboardButton(
                text=str(pos + 1), callback_data=row.url),
        )
    builder.row(types.InlineKeyboardButton(
        text='Назад', callback_data=KeyboardCallbackData.BACK,
    ))

    return create_resizable_inline_keyboard(builder)


def get_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Что умеет этот бот', callback_data=KeyboardCallbackData.MAIN_INFO),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Связь с разработчиком', callback_data=KeyboardCallbackData.DEVELOPMENT_COMMUNICATION),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data=KeyboardCallbackData.BACK),
    )

    return create_resizable_inline_keyboard(builder)


def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data=KeyboardCallbackData.BACK),
    )

    return create_resizable_inline_keyboard(builder)


def get_user_info_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Города', callback_data=KeyboardCallbackData.CITIES),
        types.InlineKeyboardButton(
            text='Трек-листы', callback_data=KeyboardCallbackData.LINKS),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data=KeyboardCallbackData.BACK),
    )

    return create_resizable_inline_keyboard(builder)


def get_tools_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Показать возможные концерты', callback_data=KeyboardCallbackData.SHOW_CONCERTS),
    )
    # builder.row(
    #     types.InlineKeyboardButton(
    #         text='Показ уведомлений', callback_data='notice_management'),
    # )
    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data=KeyboardCallbackData.BACK),
    )

    return create_resizable_inline_keyboard(builder)


def get_notify_management_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_enabled:
        builder.row(
            types.InlineKeyboardButton(
                text='Отключить', callback_data=KeyboardCallbackData.DISABLE),
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text='Включить', callback_data=KeyboardCallbackData.ENABLE),
        )

    builder.row(
        types.InlineKeyboardButton(
            text='Назад', callback_data=KeyboardCallbackData.BACK),
    )

    return create_resizable_inline_keyboard(builder)
