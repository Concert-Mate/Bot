from pydantic import BaseModel


class Playlist(BaseModel):
    url: str
    title: str
