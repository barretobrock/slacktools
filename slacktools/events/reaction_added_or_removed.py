"""
Docs: https://api.slack.com/events/emoji_changed
"""
import enum
from slacktools.events.types import (
    ReactionEventType
)
from slacktools.events.base import (
    BaseEvent,
    EventItem
)


class ReactionType(enum.Enum):
    reaction_added = 0
    reaction_removed = 1


class ReactionEvent(BaseEvent):
    """The base of the emoji_changed event classes"""
    user: str
    reaction: str
    item_user: str
    item: EventItem
    event_ts: str

    def __init__(self, event_dict: ReactionEventType):
        super().__init__(event_dict=event_dict)
        self.item = EventItem(event_dict=event_dict.get('item'))
