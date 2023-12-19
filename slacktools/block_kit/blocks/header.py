from typing import (
    List,
    Union,
)

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.text import PlainTextElement


class HeaderBlock(BaseElement):
    """
    https://api.slack.com/reference/block-kit/blocks#header
    """
    type: str = 'header'
    text: PlainTextElement
    block_id: str

    def __init__(self, text: PlainTextElement, block_id: str = None):
        self.text = text
        if block_id is not None:
            self.block_id = block_id

        super().__init__(type=self.type)
        self.length_assertion(self.text.text, 'header_text', 10)


class PlainTextHeaderBlock(HeaderBlock):

    def __init__(self, text: Union[str, List[str]], block_id: str = None):
        self.text = PlainTextElement(text=text)
        if block_id is not None:
            self.block_id = block_id

        super().__init__(self.text, block_id=block_id)
