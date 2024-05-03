from typing import Optional

from pydantic import BaseModel, Field

from model.playlist import Playlist
from .response_status import ResponseStatus


class UserTrackListsResponse(BaseModel):
    status: ResponseStatus
    tracks_lists: list[Playlist]


class UserTrackListResponse(BaseModel):
    status: ResponseStatus
    tracks_list: Optional[Playlist]
