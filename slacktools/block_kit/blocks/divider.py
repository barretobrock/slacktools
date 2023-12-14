from slacktools.block_kit.base import BaseElement


class DividerBlock(BaseElement):
    """
    https://api.slack.com/reference/block-kit/blocks#divider
    """
    type: str = 'divider'

    def __init__(self):
        super().__init__(type=self.type)
