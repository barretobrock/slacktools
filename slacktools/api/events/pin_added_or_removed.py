"""
Docs: https://api.slack.com/events/emoji_changed
"""
import enum
from typing import Optional

from slacktools.api.events.base import BaseEvent
from slacktools.api.events.types import PinEventType


class PinType(enum.Enum):
    pin_added = 0
    pin_removed = 1


class PinMessage:
    user: Optional[str]
    username: str
    bot_id: Optional[str]


class PinEventItem:
    message: PinMessage


class PinEvent(BaseEvent):
    """The base of the emoji_changed event classes"""
    user: str
    reaction: str
    item_user: str
    item: PinEventItem
    event_ts: str

    def __init__(self, event_dict: PinEventType):
        super().__init__(event_dict=event_dict)
