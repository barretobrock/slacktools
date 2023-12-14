from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.text import PlainTextElement


class ImageBlock(BaseElement):
    type: str = 'image'
    image_url: str
    alt_text: str
    title: PlainTextElement
    block_id: str

    def __init__(self, image_url: str, alt_text: str = '', title: PlainTextElement = None, block_id: str = None):
        if title is not None:
            self.title = title
        if block_id is not None:
            self.block_id = block_id
        super().__init__(image_url=image_url, alt_text=alt_text, type=self.type)
