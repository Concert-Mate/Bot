import asyncio
import logging
import sys
import threading

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot import handlers
from services.broker import Broker, RabbitMQBroker, BrokerEvent, BrokerException
from services.user_service.impl.agent_impl import UserServiceAgentImpl
from settings import settings


async def on_message(event: BrokerEvent) -> None:
    logging.info(f'Received event for user {event.user.telegram_id} with {len(event.concerts)} concert(s)')


async def on_error(exception: Exception) -> None:
    logging.error('An error with broker occurred: %s' % exception)


async def broker_listening() -> None:
    try:
        rabbitmq_broker: Broker = RabbitMQBroker()
        await rabbitmq_broker.connect(
            queue_name=settings.rabbitmq_queue,
            user_name=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
        )

        logging.info('Starting listening broker ...')
        await rabbitmq_broker.start_listening(
            on_message_callback=on_message,
            on_error_callback=on_error,
        )
    except BrokerException as e:
        logging.warning(e)


async def main() -> None:
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties())
    agent = UserServiceAgentImpl(
        user_service_host=settings.user_service_host,
        user_service_port=settings.user_service_port,
    )

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties())
    dp = Dispatcher()
    dp.include_router(handlers.common_router)
    dp.include_router(handlers.registration_router)
    dp.include_router(handlers.menu_router)
    dp.include_router(handlers.change_data_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    threading.Thread(target=asyncio.run, args=(broker_listening(),)).start()
    asyncio.run(main())