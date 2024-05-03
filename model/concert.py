from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .artist import Artist
from .price import Price


class Concert(BaseModel):
    title: str
    afisha_url: str
    city: Optional[str]
    place: Optional[str]
    address: Optional[str]
    concert_datetime: Optional[datetime] = Field(validation_alias='datetime')
    map_url: Optional[str]
    images: list[str]
    min_price: Optional[Price]
    artists: list[Artist]
