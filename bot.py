import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot import handlers
from services.user_service import UserServiceAgent
from services.user_service.impl.agent_impl import UserServiceAgentImpl
from settings import settings

bot = Bot(token=settings.bot_token, default=DefaultBotProperties())
dp = Dispatcher()
dp.include_router(handlers.common_router)
dp.include_router(handlers.registration_router)
dp.include_router(handlers.menu_router)
dp.include_router(handlers.change_data_router)


async def main() -> None:
    agent: UserServiceAgent = UserServiceAgentImpl(
        user_service_host=settings.user_service_host,
        user_service_port=settings.user_service_port,
    )

    dp['agent'] = agent

    await agent.create_user(704578790)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
