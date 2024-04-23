from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from settings import Settings


def create_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot_token, default=DefaultBotProperties())
