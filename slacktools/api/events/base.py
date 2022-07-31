from typing import Dict

from slacktools.api.base import BaseApiObject
from slacktools.api.events.types import EventItemType


class BaseEvent(BaseApiObject):
    """The base of the event classes"""
    type: str

    def __init__(self, event_dict: Dict):
        super().__init__(event_dict=event_dict)


class EventItem(BaseEvent):
    channel: str
    ts: str

    def __init__(self, event_dict: EventItemType):
        super().__init__(event_dict=event_dict)
