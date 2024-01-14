
from slacktools.block_kit.base import (
    BaseElement,
    random_string,
)
from slacktools.block_kit.elements.display.text import PlainTextElement


class ConfirmElement(BaseElement):
    """https://api.slack.com/reference/block-kit/composition-objects#confirm"""
    title: PlainTextElement
    text: PlainTextElement
    confirm: PlainTextElement
    deny: PlainTextElement
    style: str

    def __init__(self, title: str, text: str, confirm: str, deny: str, style: str = None):
        self.title = PlainTextElement(title)
        self.text = PlainTextElement(text)
        self.confirm = PlainTextElement(confirm)
        self.deny = PlainTextElement(deny)
        if style is not None:
            self.style = style
        super().__init__()


class ButtonElement(BaseElement):
    """https://api.slack.com/reference/block-kit/block-elements#button"""
    type: str = 'button'
    text: PlainTextElement
    action_id: str = 'button_action'
    block_id: str
    url: str
    value: str
    style: str
    confirm: ConfirmElement

    def __init__(self, text: str, action_id: str = action_id, url: str = None, value: str = None, style: str = None,
                 confirm: ConfirmElement = None, block_id: str = None):
        self.text = PlainTextElement(text=text)
        self.action_id = action_id
        if block_id is None:
            self.block_id = random_string()
        else:
            self.block_id = f'{random_string()}-{block_id}'
        if url is not None:
            self.url = url
        if value is not None:
            self.value = value
        if style is not None:
            self.style = style
        if confirm is not None:
            self.confirm = confirm
        super().__init__(type=self.type)
