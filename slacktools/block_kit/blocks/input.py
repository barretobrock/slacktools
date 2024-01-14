from typing import Union

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.text import PlainTextElement
from slacktools.block_kit.elements.input.text import (
    DispatchActionConfigElement,
    PlaintTextInputElement,
)

InputElementType = Union[PlaintTextInputElement]


class InputBlock(BaseElement):
    """
    https://api.slack.com/reference/block-kit/blocks#actions
    """
    type: str = 'input'
    label: PlainTextElement
    elements: InputElementType
    dispatch_action: bool = False
    hint: PlainTextElement
    optional: bool = False
    block_id: str

    def __init__(self, label: PlainTextElement, element: InputElementType, dispatch_action: bool = False,
                 block_id: str = None, hint: PlainTextElement = None, optional: bool = False):

        self.element = element
        self.label = label
        self.dispatch_action = dispatch_action
        self.optional = optional
        if block_id is not None:
            self.block_id = block_id
        if hint is not None:
            self.hint = hint

        super().__init__(type=self.type)
        self.length_assertion(self.label.text, 'label.text', 2000)


class PlainTextInputBlock(InputBlock):

    def __init__(self, label: str, action_id: str, initial_value: str = None, multiline: bool = False,
                 min_length: int = None, max_length: int = None, focus_on_load: bool = False, placeholder: str = None,
                 dispatch_action_elem: DispatchActionConfigElement = None, hint: str = None):
        label = PlainTextElement(text=label)
        if placeholder is not None:
            placeholder = PlainTextElement(text=placeholder)
        if hint is not None:
            hint = PlainTextElement(text=hint)
        element = PlaintTextInputElement(action_id=action_id, initial_value=initial_value, multiline=multiline,
                                         min_length=min_length, max_length=max_length, focus_on_load=focus_on_load,
                                         placeholder=placeholder, dispatch_action_config=dispatch_action_elem)
        super().__init__(label=label, element=element, dispatch_action=dispatch_action_elem is not None, hint=hint)
