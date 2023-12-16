from typing import (
    Dict,
    List,
)

from slacktools.api.base import BaseApiObject
from slacktools.api.web.users import UserInfo


class UserProfileChanged(BaseApiObject):
    type: str = 'user_profile_changed'
    user: UserInfo
    cache_ts: str
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'


class UserStatusChanged(BaseApiObject):
    type: str = 'user_status_changed'
    user: UserInfo
    cache_ts: str
    event_ts: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'


class UserTyping(BaseApiObject):
    """RTM Only"""
    type: str = 'user_typing'
    user: str
    channel: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'
