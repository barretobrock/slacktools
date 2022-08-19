from typing import (
    Dict,
    List,
    TypedDict,
)


class BaseApiType(TypedDict):
    type: str


class PinApiMessageItemType(BaseApiType, total=False):
    text: str
    user: str
    bot_id: str
    ts: str
    team: str
    blocks: List[Dict]
    pinned_to: List[str]
    permalink: str


class PinApiObjectType(BaseApiType):
    created: int
    created_by: str
    channel: str
    message: PinApiMessageItemType
