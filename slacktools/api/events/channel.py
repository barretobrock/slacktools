from typing import (
    Dict,
    Optional,
)

from slacktools.api.base import BaseApiObject


class Channel(BaseApiObject):
    id: str
    name: str
    created: int
    creator: Optional[str]

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)
        if 'creator' not in event_dict.keys():
            # Handled for channel_rename
            self.creator = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(name={self.name})>'


class ChannelCreated(BaseApiObject):
    type: str = 'channel_created'
    channel: Channel

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'


class ChannelArchive(BaseApiObject):
    type: str = 'channel_archive'
    channel: str
    user: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'


class ChannelUnarchive(BaseApiObject):
    type: str = 'channel_unarchive'
    channel: str
    user: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'


class ChannelRename(BaseApiObject):
    type: str = 'channel_rename'
    channel: Channel

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}()>'
