from typing import (
    Dict,
    List,
)

from slacktools.api.base import BaseApiObject

from .types import PinApiObjectType


class PinApiMessageItem:
    type: str   # 'message'
    text: str
    user: str   # user id / author
    ts: str
    blocks: List[Dict]
    pinned_to: List[str]  # List[channel_id]
    permalink: str


class PinApiObject(BaseApiObject):
    type: str
    created: int
    created_by: str  # user id
    channel: str     # channel id
    message: PinApiMessageItem

    def __init__(self, event_dict: PinApiObjectType):
        super().__init__(event_dict=event_dict)
