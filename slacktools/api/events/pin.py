from typing import (
    Dict,
    List,
    Optional,
)

from slacktools.api.base import BaseApiObject


class PinItemMessage(BaseApiObject):
    permalink: str
    pinned_to: List[str]
    text: str
    ts: str
    type: str
    user: str
    username: str
    blocks: Optional[List[Dict]]
    bot_id: Optional[str]


class PinItem(BaseApiObject):
    """When the reaction item is a message"""
    type: str
    channel: str
    created: str
    created_by: str
    message: PinItemMessage

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)


class PinAdded(BaseApiObject):
    type: str = 'pin_added'
    user: str
    channel_id: str
    item: PinItem
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)


class PinRemoved(BaseApiObject):
    type: str = 'pin_removed'
    user: str
    channel_id: str
    item: PinItem
    has_pins: bool
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)
