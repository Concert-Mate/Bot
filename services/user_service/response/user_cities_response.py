from pydantic import BaseModel

from .response_status import ResponseStatus


class UserCitiesResponse(BaseModel):
    status: ResponseStatus
    cities: list[str]
