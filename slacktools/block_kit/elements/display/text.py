from typing import (
    Dict,
    List,
    Optional,
    TypedDict,
    Union
)
from slacktools.block_kit.base import BaseElement


class PlainTextElement(BaseElement):
    """
    https://api.slack.com/reference/block-kit/composition-objects#text
    """
    type: str = 'plain_text'
    text: str
    emoji: bool = True

    def __init__(self, text: Union[str, List[str]], emoji: bool = True, joiner: str = '\n'):
        if isinstance(text, list):
            text = joiner.join(text)
        super().__init__(text=text, emoji=emoji, type=self.type)
        self.length_assertion(self.text, 'text', 3000)


class MarkdownTextElement(BaseElement):
    """
    https://api.slack.com/reference/block-kit/composition-objects#text

    NB: setting 'verbatim' to True will stop converting url-like text to actual urls.
        It will not stop formatted urls though (e.g., <url|text>)
    """
    type: str = 'mrkdwn'
    text: str
    verbatim: bool = False

    def __init__(self, text: Union[str, List[str]], joiner: str = '\n', verbatim: bool = False):
        if isinstance(text, list):
            text = joiner.join(text)
        super().__init__(text=text, type=self.type, verbatim=verbatim)
        self.length_assertion(self.text, 'text', 3000)
