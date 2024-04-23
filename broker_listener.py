import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from services.broker import Broker, BrokerEvent, BrokerException
from services.broker.impl.rabbitmq_broker import RabbitMQBroker
from settings import settings

bot = Bot(token=settings.bot_token, default=DefaultBotProperties())


async def on_message(event: BrokerEvent) -> None:
    print(f'Received message for {event.user.telegram_id}')
    await bot.send_message(chat_id=event.user.telegram_id, text=event.concerts[0].afisha_url)


async def on_error(exception: Exception) -> None:
    logging.error('An error with broker occurred: %s' % exception)


async def main() -> None:
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
