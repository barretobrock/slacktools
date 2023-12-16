from typing import Dict

from slacktools.api.base import BaseApiObject


class UserProfile(BaseApiObject):
    avatar_hash: str
    status_text: str
    status_emoji: str
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    email: str
    image_32: str
    image_512: str
    team: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(real_name="{self.real_name}")>'


class UserInfo(BaseApiObject):
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
    updated: int
    is_app_user: bool
    has_2fa: bool

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(id="{self.id}", name="{self.name}")>'
