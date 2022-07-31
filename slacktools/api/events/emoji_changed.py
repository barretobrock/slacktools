"""
Docs: https://api.slack.com/events/emoji_changed
"""
import enum
from typing import (
    List,
    Union,
)

from slacktools.api.events.base import BaseEvent
from slacktools.api.events.types import (
    EmojiAddedEventType,
    EmojiChangedEvents,
    EmojiRemovedEventType,
    EmojiRenamedEventType,
)


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


def decide_emoji_event_class(event_dict: EmojiChangedEvents) -> Union[EmojiAdded, EmojiRenamed, EmojiRemoved]:
    """Decides based on `subtype` key which emoji event class to return"""
    subtype = event_dict['subtype']
    match subtype:
        case EmojiChangeSubType.add.name:
            return EmojiAdded(event_dict=event_dict)
        case EmojiChangeSubType.remove.name:
            return EmojiRemoved(event_dict=event_dict)
        case EmojiChangeSubType.rename.name:
            return EmojiRenamed(event_dict=event_dict)
        case _:
            raise ValueError(f'Subtype not recognized: {subtype}')
