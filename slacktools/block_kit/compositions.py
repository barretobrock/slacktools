from typing import (
    List,
    Tuple,
    TypedDict
)
from slacktools.block_kit.base import (
    BaseBlock,
    MarkdownTextObjectType,
    PlainTextObjectType
)


class ConfirmationDialogType(TypedDict):
    title: PlainTextObjectType
    text: MarkdownTextObjectType
    confirm: PlainTextObjectType
    deny: PlainTextObjectType
    style: str


class OptionType(TypedDict):
    text: MarkdownTextObjectType
    value: str
    description: PlainTextObjectType
    url: str


class OptionGroupType(TypedDict):
    label: PlainTextObjectType
    options: List[OptionType]


class CompositionObjects(BaseBlock):
    """https://api.slack.com/reference/block-kit/composition-objects#confirm"""

    @classmethod
    def make_confirm_object(cls, title: str = 'Are you sure?', text: str = 'Are you sure you want to do this?',
                            confirm_text: str = 'Confirm', deny_text: str = 'Cancel', is_danger: bool = False) -> \
            ConfirmationDialogType:
        """Makes a confirmation dialog object """
        cls.perform_assertions({
            'title': (title, 100),
            'text': (text, 300),
            'confirm': (confirm_text, 30),
            'deny': (deny_text, 30),
        })

        confirm_obj = {
            'title': cls.plaintext_section(text=title),
            'text': cls.markdown_section(text=text),
            'confirm': cls.plaintext_section(text=confirm_text),
            'deny': cls.plaintext_section(text=deny_text),
            'style': 'danger' if is_danger else 'primary'
        }
        return confirm_obj

    @classmethod
    def make_option_object(cls, text: str, value: str, description: str = None, url: str = None) -> OptionType:
        cls.perform_assertions({
            'text': (text, 75),
            'value': (value, 75),
            'description': (description, 75),
            'url': (url, 3000)
        })
        option_obj = {
            'text': cls.markdown_section(text=text),
            'value': value
        }
        if description is not None:
            option_obj['description'] = cls.plaintext_section(text=description)
        if url is not None:
            option_obj['url'] = url
        return option_obj

    @classmethod
    def make_option_group(cls, label: str, options: List[Tuple]) -> OptionGroupType:
        """NB! Option groups are only used in select or multi-select menus"""
        cls.perform_assertions({
            'label': (label, 75),
            'options ': (options, 100),
        })
        return {
            'label': cls.plaintext_section(text=label),
            'options': [cls.make_option_object(*x) for x in options]
        }
