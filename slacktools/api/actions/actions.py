from typing import (
    Dict,
    List,
    Optional,
)

from slacktools.api.base import BaseApiObject
from slacktools.api.web.conversations import Message


class Team(BaseApiObject):
    id: str
    domain: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class TextItem(BaseApiObject):
    type: str
    text: str
    emoji: bool

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class User(BaseApiObject):
    id: str
    username: str
    team_id: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class Container(BaseApiObject):
    type: str = 'message_attachment'
    message_ts: str
    attachment_id: int
    channel_id: str
    is_emphemeral: bool
    is_app_unfurl: bool

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class Channel(BaseApiObject):
    id: str
    name: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class ActionMessage(Message):
    bot_id: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class Action(BaseApiObject):
    action_id: str
    block_id: str
    text: TextItem
    value: str
    type: str
    action_ts: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class ButtonAction(Action):
    type: str = 'button'

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class SelectOption(BaseApiObject):
    value: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class MultiSelectAction(Action):
    type: str = 'multi_static_select'
    selected_options: List[SelectOption]

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class SelectUserAction(Action):
    selected_user: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class MultiSelectUserAction(Action):
    selected_users: List[str]

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class ShortcutAction(Action):
    type: str = 'message-shortcut'

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)


class BlockAction(BaseApiObject):
    type: str = 'block_actions'
    team: Team
    user: User
    api_app_id: str
    token: str
    container: Container
    trigger_id: str
    channel: Channel
    message: Message
    response_url: str
    actions: List[Action]
    # Not part of original resp
    action: Optional[Action]

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)
        self.action = self.actions[0]
        # TODO: Determine action type and fill in `action_type`?

    def get_action_id(self) -> Optional[str]:
        """Actions always seems to be a list of len 1, so just return either the first action id or None"""
        return next((a.action_id for a in self.actions), None)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(n_actions="{len(self.actions)}", action_id="{self.get_action_id()}")>'
