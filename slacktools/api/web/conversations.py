from typing import (
    Dict,
    List,
    Optional,
)

from slacktools.api.base import (
    BaseApiObject,
    ResponseMetadata,
)


class ConversationMembers(BaseApiObject):
    members: List[str]
    response_metadata: ResponseMetadata

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(members={self.members})>'


class MessageAttachment(BaseApiObject):
    service_name: str
    text: str
    fallback: str
    thumb_url: str
    thumb_width: int
    thumb_height: int
    id: int

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(service_name={self.service_name})>'


class Reaction(BaseApiObject):
    name: str
    users: List[str]
    count: int


class Message(BaseApiObject):
    type: str
    user: str
    text: str
    ts: str
    attachments: Optional[List[MessageAttachment]]
    reactions: Optional[List[Reaction]]

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(ts={self.ts})>'


class ThreadMessage(Message):
    thread_ts: str
    parent_user_id: str

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(ts={self.ts})>'


class ConversationReply(BaseApiObject):
    messages: List[ThreadMessage]
    has_more: bool
    response_metadata: ResponseMetadata

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(messages={self.messages})>'


class ConversationHistory(BaseApiObject):
    messages: List[Message]
    has_more: bool
    pin_count: int
    response_metadata: ResponseMetadata
    latest: Optional[str]

    def __init__(self, resp_dict: Dict = None, **kwargs):
        super().__init__(resp_dict, **kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(messages={self.messages})>'
