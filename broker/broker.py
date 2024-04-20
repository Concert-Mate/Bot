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
        pass

    @abstractmethod
    async def start_listening(
            self,
            on_message_callback: Callable[[BrokerEvent], Coroutine[Any, Any, None]],
            on_error_callback: Callable[[Exception], Coroutine[Any, Any, None]]
    ) -> None:
        pass
