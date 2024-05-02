from pydantic import BaseModel, Field

from .response_status_code import ResponseStatusCode


class ResponseStatus(BaseModel):
    code: ResponseStatusCode
    message: str
    is_success: bool = Field(validation_alias='is_success')
