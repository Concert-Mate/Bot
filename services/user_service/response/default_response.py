from pydantic import BaseModel

from .response_status import ResponseStatus


class DefaultResponse(BaseModel):
    status: ResponseStatus
