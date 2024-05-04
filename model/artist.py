from pydantic import BaseModel, Field


class Artist(BaseModel):
    name: str
    yandex_music_id: int
