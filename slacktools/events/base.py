from typing import Dict

from slacktools.events.types import EventItemType


class BaseEvent:
    """The base of the event classes"""
    type: str

    def __init__(self, event_dict: Dict):
        for k, v in event_dict.items():
            if isinstance(v, dict):
                continue
            self.__setattr__(k, v)


class EventItem(BaseEvent):
    channel: str
    ts: str

    def __init__(self, event_dict: EventItemType):
        super().__init__(event_dict=event_dict)
