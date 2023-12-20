from typing import (
    Dict,
    List,
    Optional,
)

from slacktools.api.base import BaseApiObject


class EditedMessage:
    user: str
    ts: str


class Message(BaseApiObject):
    type: str = 'message'
    subtype: Optional[str]  # channel_join, message_deleted
    channel: str
    channel_type: str  # channel, im, group
    user: str
    text: str
    blocks: Optional[List[Dict]]
    ts: str
    event_ts: str
    edited: Optional[EditedMessage]
    # Not part of the actual response
    channel_id: str
    thread_ts: str
    raw_text: str
    raw_message: str
    message_hash: str
    cleaned_message: str
    match_pattern: str

    def __init__(self, event_dict: Dict = None, **kwargs):
        self.blocks = None
        self.subtype = None
        super().__init__(event_dict, **kwargs)
        self.raw_text = self.text
        self.thread_ts = self.ts
        self.channel_id = self.channel
        self.message_hash = f'{self.channel_id}_{self.event_ts}'
        self.cleaned_message = self.raw_message = self.raw_text

    def take_processed_message(self, clean_msg: str, raw_message: str):
        self.cleaned_message = clean_msg
        self.raw_message = raw_message

    def take_match_pattern(self, match_pattern: str):
        self.match_pattern = match_pattern

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(event_ts={self.event_ts})>'
