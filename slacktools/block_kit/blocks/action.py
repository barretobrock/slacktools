from typing import (
    List,
    Union,
)

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.input.button import ButtonElement

ActionsElementType = Union[ButtonElement]


class ActionsBlock(BaseElement):
    """
    https://api.slack.com/reference/block-kit/blocks#actions
    """
    type: str = 'actions'
    elements: List[ActionsElementType]
    block_id: str

    def __init__(self, elements: List[ActionsElementType], block_id: str = None):

        self.elements = elements
        if block_id is not None:
            self.block_id = block_id

        super().__init__(type=self.type)
        self.length_assertion(self.elements, 'elements', 25)
