from typing import Optional

from slacktools.api.events.base import BaseEvent
from slacktools.api.events.types import AllMessageEventTypes


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

    def __init__(self, event_dict: AllMessageEventTypes):
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
