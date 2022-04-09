from typing import Dict


class UserSlass:
    """A class object for a given slack user"""

    user_hash = None            # type: str
    email_name = None           # type: str
    full_name = None            # type: str
    display_name = None         # type: str
    is_bot = None               # type: bool
    title = None                # type: str
    status_emoji = None         # type: str
    status_text = None          # type: str
    avatar_hash = None          # type: str
    avatar_link_512px = None    # type: str
    avatar_link_32px = None     # type: str

    # Mapping to map keys to attributes
    SLACK_TO_SLASS = {
        'id': 'user_hash',
        'name': 'email_name',
        'real_name': 'full_name',
        'display_name': 'display_name',
        'is_bot': 'is_bot',
        'title': 'title',
        'status_emoji': 'status_emoji',
        'status_text': 'status_text',
        'avatar_hash': 'avatar_hash',
        'image_512': 'avatar_link_512',
        'image_32': 'avatar_link_32',
    }

    def __init__(self, user_dict: Dict):
        self._intake_dict(user_dict)

    def _intake_dict(self, some_dict: Dict):
        for k, v in some_dict.items():
            if isinstance(v, dict):
                self._intake_dict(v)
            elif k in self.SLACK_TO_SLASS.keys():
                self.__setattr__(self.SLACK_TO_SLASS[k], v)
