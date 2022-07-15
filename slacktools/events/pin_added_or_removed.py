"""
Docs: https://api.slack.com/events/emoji_changed
"""
import enum

from slacktools.events.base import (
    BaseEvent,
    EventItem,
)
from slacktools.events.types import PinEventType


class PinType(enum.Enum):
    pin_added = 0
    pin_removed = 1


class PinEvent(BaseEvent):
    """The base of the emoji_changed event classes"""
    user: str
    reaction: str
    item_user: str
    item: EventItem
    event_ts: str

    def __init__(self, event_dict: PinEventType):
        super().__init__(event_dict=event_dict)
        self.item = EventItem(event_dict=event_dict.get('item'))
