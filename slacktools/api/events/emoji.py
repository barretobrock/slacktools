from typing import (
    Dict,
    List,
)

from slacktools.api.base import BaseApiObject


class EmojiRenamed(BaseApiObject):
    type: str = 'emoji_changed'
    subtype: str = 'rename'
    old_name: str
    new_name: str
    value: str
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'


class EmojiRemoved(BaseApiObject):
    type: str = 'emoji_changed'
    subtype: str = 'remove'
    names: List[str]
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'


class EmojiAdded(BaseApiObject):
    type: str = 'emoji_changed'
    subtype: str = 'add'
    name: str
    value: str
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'
