from pydantic import BaseModel

from model import Concert
from .response_status import ResponseStatus


class UserConcertsResponse(BaseModel):
    status: ResponseStatus
    concerts: list[Concert]
