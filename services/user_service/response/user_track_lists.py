from pydantic import BaseModel, Field

from .response_status import ResponseStatus


class UserTrackListsResponse(BaseModel):
    status: ResponseStatus
    track_lists: list[str] = Field(validation_alias='tracksLists')
