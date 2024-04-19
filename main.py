import asyncio
import logging
import sys
import threading

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import handlers
from broker import Broker, RabbitMQBroker, BrokerEvent, BrokerException
from settings import settings


def broker_listener_task(broker: Broker) -> None:
    logging.info('Starting listening broker ...')
    broker.start_listening()


def callback(event: BrokerEvent) -> None:
    print(f'Received event:\n{event}')


async def main() -> None:
    try:
        rabbitmq_broker: Broker = RabbitMQBroker(
            queue_name=settings.rabbitmq_queue,
            user_name=settings.rabbitmq_user,
            password=settings.rabbitmq_password
        )
        rabbitmq_broker.add_callback(callback)
        logging.info('Callback added')
        broker_listener = threading.Thread(target=broker_listener_task, args=(rabbitmq_broker,))
        broker_listener.start()
    except BrokerException as e:
        logging.warning(e)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties())
    dp = Dispatcher()
    dp.include_router(handlers.common_router)
    dp.include_router(handlers.registration_router)
    dp.include_router(handlers.menu_router)
    dp.include_router(handlers.change_data_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
