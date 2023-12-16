from typing import (
    Dict,
    List,
)

from slacktools.api.base import BaseApiObject


class PinMessage(BaseApiObject):
    permalink: str
    pinned_to: List[str]
    text: str
    ts: str
    type: str
    user: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(ts={self.ts})>'


class Pin(BaseApiObject):
    channel: str
    created: int
    created_by: str
    message: PinMessage
    type: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(created={self.created})>'


class PinsList(BaseApiObject):
    items: List[Pin]

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(items={len(self.items)})>'
