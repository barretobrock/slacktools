from typing import (
    List,
    Optional,
    Union,
)

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.image import ImageElement
from slacktools.block_kit.elements.display.text import (
    MarkdownTextElement,
    PlainTextElement,
)
from slacktools.block_kit.elements.input.button import ButtonElement


class SectionBlock(BaseElement):
    type: str = 'section'
    text: Union[PlainTextElement, MarkdownTextElement]
    accessory: Optional[Union[ImageElement, ButtonElement]]
    fields: Optional[List[PlainTextElement]]

    def __init__(self, text_elem: Union[PlainTextElement, MarkdownTextElement] = None,
                 accessory: Optional[Union[ImageElement, ButtonElement]] = None, fields: List[PlainTextElement] = None):

        if text_elem is None and fields is None:
            raise ValueError('One of text_elem or fields must not be empty!')
        if accessory is not None:
            self.accessory = accessory
        if fields is not None:
            self.fields = fields
            self.length_assertion(self.fields, 'fields', 10)

        self.text = text_elem
        super().__init__(type=self.type)


class PlaintextSectionBlock(SectionBlock):
    def __init__(self, text: Union[str, List[str]], joiner: str = '\n', image_url: str = None,
                 image_alt_txt: str = ''):
        accessory = None
        if image_url is not None:
            accessory = ImageElement(image_url, image_alt_txt)
        super().__init__(text_elem=PlainTextElement(text=text, joiner=joiner), accessory=accessory)


class MarkdownSectionBlock(SectionBlock):
    def __init__(self, text: Union[str, List[str]], joiner: str = '\n', image_url: str = None,
                 image_alt_txt: str = ''):
        accessory = None
        if image_url is not None:
            accessory = ImageElement(image_url, image_alt_txt)
        super().__init__(text_elem=MarkdownTextElement(text=text, joiner=joiner), accessory=accessory)


class ButtonSectionBlock(SectionBlock):
    accessory: ButtonElement

    def __init__(self, text: Union[str, List[str]], button_text: str, value: str, action_id: str = 'button_action',
                 joiner: str = '\n'):
        accessory = ButtonElement(text=button_text, action_id=action_id, value=value)
        super().__init__(text_elem=PlainTextElement(text=text, joiner=joiner), accessory=accessory)
