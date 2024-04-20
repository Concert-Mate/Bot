from pydantic import BaseModel

from .response_status import ResponseStatus


class UserTrackListsResponse(BaseModel):
    status: ResponseStatus
    track_lists: list[str]
