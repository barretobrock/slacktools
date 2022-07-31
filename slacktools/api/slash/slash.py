from typing import TypedDict

from slacktools.api.events.base import BaseEvent


class SlashCommandEventType(TypedDict):
    command: str
    text: str
    response_url: str
    trigger_id: str
    user_id: str
    user_name: str
    channel_id: str


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
