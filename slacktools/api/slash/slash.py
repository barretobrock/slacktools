from typing import Dict

from slacktools.api.base import BaseApiObject


class SlashCommandEvent(BaseApiObject):
    # Official items
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str
    response_url: str
    trigger_id: str
    # Extra items
    raw_text: str
    cleaned_message: str
    match_pattern: str
    is_in_thread: bool = False
    thread_ts: str = None

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)
        self.raw_command = self.command
        self.cleaned_command = self.command.replace('/', '').replace('-', ' ')
        # Some commands can be without prompts / additional messages
        self.cleaned_message = f'{self.cleaned_command} {self.text}' if self.text != '' else self.cleaned_command

    def take_match_pattern(self, match_pattern: str):
        self.match_pattern = match_pattern

    def __repr__(self):
        return (f'<SlashCommandEvent(cmd="{self.raw_command}", '
                f'text="{self.text[:20] if self.text is not None else ""}")>')
