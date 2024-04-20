from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    telegram_id: int = Field(validation_alias='telegramId')
    created_at: datetime = Field(validation_alias='creationDatetime')
