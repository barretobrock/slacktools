from typing import List

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.text import PlainTextElement


class DispatchActionConfigElement(BaseElement):
    trigger_actions_on: List[str]

    def __init__(self, trigger_on_enter_pressed: bool = False, trigger_on_character_entered: bool = False):
        on_enter = 'on_enter_pressed'
        on_char = 'on_character_entered'
        trigger_actions = []
        if trigger_on_enter_pressed:
            trigger_actions.append(on_enter)
        if trigger_on_character_entered:
            trigger_actions.append(on_char)
        self.trigger_actions_on = trigger_actions

        super().__init__()


class PlaintTextInputElement(BaseElement):
    """https://api.slack.com/reference/block-kit/block-elements#input"""
    type: str = 'plain_text_element'
    action_id: str = 'plaintext-input-action'
    initial_value: str
    multiline: bool = False
    min_length: int
    max_length: int
    dispatch_action_config: DispatchActionConfigElement
    focus_on_load: bool = False
    placeholder: PlainTextElement

    def __init__(self, action_id: str = action_id, initial_value: str = None, multiline: bool = False,
                 min_length: int = None, max_length: int = None, focus_on_load: bool = False,
                 placeholder: PlainTextElement = None, dispatch_action_config: DispatchActionConfigElement = None):
        self.action_id = action_id
        self.multiline = multiline
        self.focus_on_load = focus_on_load
        if initial_value is not None:
            self.initial_value = initial_value
        if min_length is not None:
            self.min_length = min_length
        if max_length is not None:
            self.max_length = max_length
        if placeholder is not None:
            self.placeholder = placeholder
            self.length_assertion(self.placeholder.text, 'placeholder.text', 150)
        if dispatch_action_config is not None:
            self.dispatch_action_config = dispatch_action_config

        super().__init__(type=self.type)
