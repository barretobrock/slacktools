from typing import TypedDict
from slacktools.block_kit.base import BaseElementType


class DividerType(BaseElementType, total=False):
    block_id: str


def make_divider_block(block_id: str = None) -> DividerType:
    """Returns a dict that renders a divider in Slack's Block Kit
    Docs: https://api.slack.com/reference/block-kit/blocks#divider
    """
    div = {
        'type': 'divider'
    }
    if block_id is not None:
        div['block_id'] = block_id
    return div
