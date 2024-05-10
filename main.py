import asyncio
import logging
from logging import config

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot import handlers
from bot.handlers.throttling_protection import AntiFloodMiddleware, AntiFloodMiddlewareM
from services.user_service import UserServiceAgent
from services.user_service.impl.agent_impl import UserServiceAgentImpl
from settings import settings
from utils import create_bot


async def main() -> None:
    agent: UserServiceAgent = UserServiceAgentImpl(
        user_service_host=settings.user_service_host,
        user_service_port=settings.user_service_port,
    )

    # TODO: сделать логирование в обработке ответов от бэкенда

    storage = RedisStorage.from_url(f'redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}')

    try:
        await storage.redis.ping()
        root_logger.info('Connection with redis on bot is OK')
    except Exception as e:
        root_logger.error(msg=f'No connection with redis on bot. {str(e)}')
        return

    bot: Bot = create_bot(settings)
    dp = Dispatcher(storage=storage)
    dp['agent'] = agent

    dp.include_router(handlers.common_router)
    dp.callback_query.middleware(AntiFloodMiddleware())
    dp.message.middleware(AntiFloodMiddlewareM())

    dp.include_router(handlers.registration_router)
    dp.include_router(handlers.menu_router)
    dp.include_router(handlers.change_data_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.config.fileConfig(fname='logging.ini')
    root_logger = logging.getLogger('root')
    asyncio.run(main())
