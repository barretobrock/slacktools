from typing import (
    Optional,
    Union,
)

from slacktools.events.base import BaseEvent
from slacktools.events.types import (
    SlashCommandEventType,
    StandardMessageEventType,
    ThreadedMessageEventType,
)


class MessageEvent(BaseEvent):
    subtype: Optional[str]
    thread_ts: Optional[str]
    raw_text: str
    raw_message: str
    cleaned_message: str
    channel_id: str
    event_ts: str
    user_id: str
    message_hash: str
    match_pattern: Optional[str]

    def __init__(self, event_dict: Union[StandardMessageEventType, ThreadedMessageEventType]):
        # Keep 'ts' from becoming an attribute - it's confusingly named as to what timestamp it refers
        self.event_ts = event_dict.pop('ts')
        self.user_id = event_dict.pop('user')
        super().__init__(event_dict=event_dict)
        if 'subtype' not in event_dict.keys():
            self.subtype = None
        self.raw_text = event_dict['text']

        self.channel_id = event_dict['channel']
        self.thread_ts = event_dict.get('thread_ts')
        self.message_hash = f'{self.channel_id}_{self.event_ts}'

    def take_processed_message(self, clean_msg: str, raw_message: str):
        """Takes in a processed message"""
        self.cleaned_message = clean_msg
        self.raw_message = raw_message

    def take_match_pattern(self, match_pattern: str):
        self.match_pattern = match_pattern

    def __repr__(self):
        return f'<MessageEvent(subtype="{self.subtype}", text={self.raw_text[:20]})>'


class SlashCommandEvent(BaseEvent):
    raw_command: str
    text: str
    response_url: str
    trigger_id: str
    user_id: str
    user_name: str
    channel_id: str

    def __init__(self, event_dict: SlashCommandEventType):
        # Keep 'ts' from becoming an attribute - it's confusingly named as to what timestamp it refers
        super().__init__(event_dict=event_dict)
        self.cleaned_command = self.raw_command.replace('/', '').replace('-', ' ')
        # Some commands can be without prompts / additional messages
        self.full_message = f'{self.cleaned_command} {self.text}' if self.text != '' else self.cleaned_command

    def __repr__(self):
        return f'<SlashCommandEvent(cmd="{self.raw_command}", text="{self.text[:20]}")>'
