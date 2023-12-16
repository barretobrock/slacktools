from typing import (
    Dict,
    Union,
)

from slacktools.api.base import BaseApiObject


class ReactionItemMessage(BaseApiObject):
    """When the reaction item is a message"""
    type: str
    channel: str
    ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(ts={self.ts})>'


class ReactionItemFile(BaseApiObject):
    """When the reaction item is a message"""
    type: str
    file: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'


class ReactionAdded(BaseApiObject):
    type: str = 'reaction_added'
    user: str
    reaction: str   # No leading/trailing colon
    item_user: str  # User that created the original item
    item: Union[ReactionItemMessage, ReactionItemFile]
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'


class ReactionRemoved(BaseApiObject):
    type: str = 'reaction_removed'
    user: str
    reaction: str   # No leading/trailing colon
    item_user: str  # User that created the original item
    item: Union[ReactionItemMessage, ReactionItemFile]
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'
