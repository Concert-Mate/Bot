from abc import ABC, abstractmethod
from typing import Coroutine, Callable, Any

from .event import BrokerEvent


class Broker(ABC):
    @abstractmethod
    async def connect(
            self,
            queue_name: str,
            user_name: str,
            password: str,
            host: str,
            port: int
    ) -> None:
        """
        Connects to broker.

        :param queue_name: name of broker's queue of messages.
        :param user_name: name of broker user
        :param password: password of broker user
        :param host: host of broker
        :param port: port of broker
        :raises BrokerException: if connection fails
        """
        pass

    @abstractmethod
    async def start_listening(
            self,
            on_message_callback: Callable[[BrokerEvent], Coroutine[Any, Any, None]],
            on_error_callback: Callable[[Exception], Coroutine[Any, Any, None]]
    ) -> None:
        """
        Thread that calls it starts listening messages from broker.

        :param on_message_callback: coroutine that will be awaited when a message is received
        :param on_error_callback: coroutine that will be awaited when an error occurs
        """
        pass
