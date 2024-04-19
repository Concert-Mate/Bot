from json import loads
from typing import Callable

from pika import PlainCredentials, ConnectionParameters, BlockingConnection, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic

from broker import Broker, BrokerException, BrokerEvent


class RabbitMQBroker(Broker):
    __channel: BlockingChannel
    __queue_name: str

    def __init__(self, queue_name: str, user_name: str, password: str, host: str = 'localhost', port: int = 5672):
        self.__queue_name = queue_name
        credentials = PlainCredentials(
            username=user_name,
            password=password
        )
        parameters = ConnectionParameters(host=host, port=port, credentials=credentials)

        try:
            connection = BlockingConnection(parameters)
            self.__channel = connection.channel()
        except Exception as e:
            raise BrokerException('Cannot connect to RabbitMQ') from e

    def add_callback(self, on_message_callback: Callable[[BrokerEvent], None]) -> None:
        def wrapper(_: BlockingChannel, __: Basic.Deliver, ___: BasicProperties, bytez: bytes) -> None:
            try:
                message: str = bytez.decode()
                event: BrokerEvent = BrokerEvent(**loads(message))
                on_message_callback(event)
            except UnicodeDecodeError as e:
                raise BrokerException('Received invalid message') from e
            except Exception as e:
                raise BrokerException('Cannot parse message') from e

        self.__channel.basic_consume(
            queue=self.__queue_name,
            on_message_callback=wrapper,
            auto_ack=True
        )

    def start_listening(self) -> None:
        try:
            self.__channel.start_consuming()
        except Exception as e:
            raise BrokerException('Cannot start listening to RabbitMQ') from e
