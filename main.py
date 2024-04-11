import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import src.handlers as handlers


async def main() -> None:

    print('successful launch')
    token = getenv('BOT_TOKEN')
    if token is None:
        print('bot token not')
        return
    bot = Bot(token=token, default=DefaultBotProperties())
    dp = Dispatcher()
    dp.include_router(handlers.common_router)
    dp.include_router(handlers.registration_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
