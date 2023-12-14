from slacktools.block_kit.base import BaseElement


class ImageElement(BaseElement):
    """https://api.slack.com/reference/block-kit/block-elements#image"""
    type: str = 'image'
    image_url: str
    alt_text: str

    def __init__(self, image_url: str, alt_text: str = ''):
        super().__init__(image_url=image_url, alt_text=alt_text, type=self.type)
