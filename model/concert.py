from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .artist import Artist
from .price import Price


class Concert(BaseModel):
    title: str
    afisha_url: str = Field(validation_alias='afishaUrl')
    city: Optional[str]
    place: Optional[str]
    address: Optional[str]
    datetime: Optional[datetime]
    map_url: Optional[str] = Field(validation_alias='mapUrl')
    images: list[str]
    min_price: Optional[Price] = Field(validation_alias='minPrice')
    artists: list[Artist]
