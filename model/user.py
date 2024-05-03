from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    telegram_id: int
    created_at: datetime = Field(validation_alias='creation_datetime')
