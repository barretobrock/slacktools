"""
Docs: https://api.slack.com/events/emoji_changed
"""
import enum
from typing import List
from slacktools.events.types import (
    EmojiAddedEventType,
    EmojiRenamedEventType,
    EmojiRemovedEventType,
    EmojiChangedEvents
)
from slacktools.events.base import BaseEvent


class EmojiChangeSubType(enum.Enum):
    add = 0
    rename = 1
    remove = 2


class _EmojiChanged(BaseEvent):
    """The base of the emoji_changed event classes"""
    subtype: str
    event_ts: str

    def __init__(self, event_dict: EmojiChangedEvents):
        super().__init__(event_dict=event_dict)


class EmojiAdded(_EmojiChanged):
    name: str
    value: str

    def __init__(self, event_dict: EmojiAddedEventType):
        super().__init__(event_dict=event_dict)


class EmojiRenamed(_EmojiChanged):
    old_name: str
    new_name: str
    value: str

    def __init__(self, event_dict: EmojiRenamedEventType):
        super().__init__(event_dict=event_dict)


class EmojiRemoved(_EmojiChanged):
    names: List[str]

    def __init__(self, event_dict: EmojiRemovedEventType):
        super().__init__(event_dict=event_dict)
