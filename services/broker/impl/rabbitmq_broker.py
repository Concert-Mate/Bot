import logging
from typing import Callable, Coroutine, Any

from aio_pika.abc import AbstractChannel, AbstractQueue
from aio_pika.connection import Connection
from yarl import URL

from services.broker import Broker, BrokerEvent, BrokerException

root_logger = logging.getLogger('root')


class RabbitMQBroker(Broker):
    __connection: Connection
    __queue_name: str

    def __init__(self) -> None:
        pass

    async def connect(
            self,
            queue_name: str,
            user_name: str,
            password: str,
            host: str,
            port: int
    ) -> None:
        try:
            url: URL = URL(f'amqp://{user_name}:{password}@{host}:{port}/')
            root_logger.debug(f'Trying to connect on amqp://{user_name}:**********@{host}:{port}/')
            self.__connection = Connection(url=url)
        except Exception as e:
            root_logger.error(f'Failed to create connection: {str(e)}')
            raise BrokerException(f'Invalid connection params') from e

        try:
            await self.__connection.connect()
            root_logger.debug(f'Successfully connected: {str(self.__connection)}')
            self.__queue_name = queue_name
        except Exception as e:
            root_logger.error(f'Failed to connect: {str(e)}')
            raise BrokerException(f'Cannot connect to {self.__connection}') from e

    async def start_listening(
            self,
            on_message_callback: Callable[[BrokerEvent], Coroutine[Any, Any, None]],
            on_error_callback: Callable[[Exception], Coroutine[Any, Any, None]]
    ) -> None:
        try:
            async with self.__connection as connection:
                root_logger.debug(f'Creating AMQP channel for connection')
                channel: AbstractChannel = await connection.channel()
                root_logger.debug(f'Channel created: {str(channel)}')
                queue: AbstractQueue = await channel.get_queue(name=self.__queue_name)
                root_logger.debug(f'Declare queue: {queue}')
                async for message in queue:
                    event: BrokerEvent = RabbitMQBroker.__parse_event(message.body)
                    await on_message_callback(event)
                    await message.ack()
        except Exception as e:
            root_logger.error(f'{str(e)}')
            await on_error_callback(e)

    @staticmethod
    def __parse_event(bytez: bytes) -> BrokerEvent:
        return BrokerEvent.model_validate_json(bytez.decode())
