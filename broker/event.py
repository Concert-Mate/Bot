from pydantic import BaseModel, Field

from model import Concert, User


class BrokerEvent(BaseModel):
    user: User
    concerts: list[Concert] = Field(min_length=1)
