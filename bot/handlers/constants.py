from aiogram import F
from aiogram.enums import ContentType
from aiogram.filters import Command

SKIP_COMMAND_FILTER = Command('skip')

TEXT_WITHOUT_COMMANDS_FILTER = F.content_type == ContentType.TEXT and F.text[0] != '/'

INTERNAL_ERROR_DEFAULT_TEXT = 'Внутренние проблемы сервиса, попробуйте позже.'

CHOOSE_ACTION_TEXT = 'Выберите действие'

MAXIMUM_CITY_LEN = 40

MAXIMUM_LINK_LEN = 100
