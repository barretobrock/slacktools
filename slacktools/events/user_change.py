"""
Docs: https://api.slack.com/events/emoji_changed
"""
from typing import Dict

from slacktools.events.base import BaseEvent
from slacktools.events.types import (
    UserChangeType,
    UserInfoType,
    UserProfileType,
)


class UserProfile(BaseEvent):
    title: str
    phone: str
    skype: str
    real_name: str
    real_name_normalized: str
    display_name: str
    display_name_normalized: str
    fields: Dict
    status_text: str
    status_emoji: str
    status_emoji_display_info: str
    status_expiration: str
    avatar_hash: str
    first_name: str
    last_name: str
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    status_text_canonical: str
    team: str

    def __init__(self, event_dict: UserProfileType):
        super().__init__(event_dict=event_dict)


class UserInfo(BaseEvent):
    id: str
    team_id: str
    name: str
    deleted: bool
    color: str
    real_name: str
    tz: str
    tz_label: str
    tz_offset: int
    profile: UserProfile
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_bot: bool
    is_app_user: bool
    updated: int
    is_email_confirmed: bool
    who_can_share_contact_card: str
    locale: str

    def __init__(self, event_dict: UserInfoType):
        super().__init__(event_dict=event_dict)
        self.profile = UserProfile(event_dict=event_dict.get('profile'))


class UserChange(BaseEvent):
    user: UserInfo
    event_ts: str
    cache_ts: int

    def __init__(self, event_dict: UserChangeType):
        super().__init__(event_dict=event_dict)
        self.user = UserInfo(event_dict=event_dict.get('user'))
