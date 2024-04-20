from pydantic import BaseModel

from model import Concert, User


class BrokerEvent(BaseModel):
    user: User
    concerts: list[Concert]
