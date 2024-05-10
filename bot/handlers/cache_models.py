from pydantic import BaseModel

from model import Concert
from model.playlist import Playlist


class CachePlaylists(BaseModel):
    track_lists: list[Playlist]


class CacheCities(BaseModel):
    cities: list[str]


class CacheConcerts(BaseModel):
    concerts: list[str]
