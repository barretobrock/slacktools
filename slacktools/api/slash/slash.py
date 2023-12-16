from typing import Dict

from slacktools.api.base import BaseApiObject


class SlashCommandEvent(BaseApiObject):
    command: str
    raw_command: str
    text: str
    response_url: str
    trigger_id: str
    user_id: str
    user_name: str
    team_id: str
    channel_id: str
    channel_name: str

    def __init__(self, event_dict: Dict, **kwargs):
        super().__init__(event_dict, **kwargs)
        self.raw_command = self.command
        self.cleaned_command = self.command.replace('/', '').replace('-', ' ')
        # Some commands can be without prompts / additional messages
        self.full_message = f'{self.cleaned_command} {self.text}' if self.text != '' else self.cleaned_command

    def __repr__(self):
        return (f'<SlashCommandEvent(cmd="{self.raw_command}", '
                f'text="{self.text[:20] if self.text is not None else ""}")>')
