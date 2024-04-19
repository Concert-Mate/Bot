from abc import ABC, abstractmethod
from typing import Callable

from .event import BrokerEvent


class Broker(ABC):
    @abstractmethod
    def add_callback(self, on_message_callback: Callable[[BrokerEvent], None]) -> None:
        pass

    @abstractmethod
    def start_listening(self) -> None:
        pass
