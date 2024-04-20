from pydantic import BaseModel


class Price(BaseModel):
    price: int
    currency: str
