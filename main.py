import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import src.handlers as handlers


async def main():
    # TODO: добавить обработку, когда прислали изображение, ГС, файл вместо геопозиции

    print('successful launch')
    bot = Bot(token=getenv('BOT_TOKEN'), default=DefaultBotProperties())
    dp = Dispatcher()
    dp.include_router(handlers.common_router)
    dp.include_router(handlers.registration_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
