from typing import Optional

from pydantic import BaseModel

from .response_status import ResponseStatus


class UserAddCityResponse(BaseModel):
    status: ResponseStatus
    variant: Optional[str] = None
