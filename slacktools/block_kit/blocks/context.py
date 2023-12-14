from typing import (
    List,
    Union,
)

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.image import ImageElement
from slacktools.block_kit.elements.display.text import (
    MarkdownTextElement,
    PlainTextElement,
)


class ContextBlock(BaseElement):
    """
    https://api.slack.com/reference/block-kit/blocks#context
    """
    type: str = 'context'
    elements: List[Union[PlainTextElement, MarkdownTextElement, ImageElement]]
    block_id: str

    def __init__(self, elements: List[Union[PlainTextElement, MarkdownTextElement, ImageElement]],
                 block_id: str = None):

        self.elements = elements
        if block_id is not None:
            self.block_id = block_id

        super().__init__(type=self.type)
        self.length_assertion(self.elements, 'elements', 10)


class PlainTextContextBlock(ContextBlock):
    def __init__(self, elements: Union[str, List[str]],
                 block_id: str = None):
        if isinstance(elements, str):
            elements = [elements]

        processed = []
        for elem in elements:
            processed.append(PlainTextElement(text=elem))
        super().__init__(elements=processed, block_id=block_id)


class MarkdownContextBlock(ContextBlock):
    def __init__(self, elements: Union[str, List[str]],
                 block_id: str = None):
        if isinstance(elements, str):
            elements = [elements]

        processed = []
        for elem in elements:
            processed.append(MarkdownTextElement(text=elem))
        super().__init__(elements=processed, block_id=block_id)
