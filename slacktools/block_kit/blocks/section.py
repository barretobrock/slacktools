from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.image import ImageElement
from slacktools.block_kit.elements.display.text import (
    MarkdownTextElement,
    PlainTextElement,
)
from slacktools.block_kit.elements.input.button import ButtonElement
from slacktools.block_kit.elements.input.select import (
    MultiStaticSelectElement,
    MultiUserSelectElement,
    OptionObject,
    StaticSelectElement,
    UserSelectElement,
)

AccessoryElementType = Union[
    ImageElement, ButtonElement, StaticSelectElement, MultiStaticSelectElement, MultiUserSelectElement,
    UserSelectElement
]


class SectionBlock(BaseElement):
    type: str = 'section'
    text: Union[PlainTextElement, MarkdownTextElement]
    accessory: Optional[AccessoryElementType]
    fields: Optional[List[PlainTextElement]]

    def __init__(self, text_elem: Union[PlainTextElement, MarkdownTextElement] = None,
                 accessory: Optional[AccessoryElementType] = None, fields: List[PlainTextElement] = None):

        if text_elem is None and fields is None:
            raise ValueError('One of text_elem or fields must not be empty!')
        if accessory is not None:
            self.accessory = accessory
        if fields is not None:
            self.fields = fields
            self.length_assertion(self.fields, 'fields', 10)

        self.text = text_elem
        super().__init__(type=self.type)


class PlainTextSectionBlock(SectionBlock):
    def __init__(self, text: Union[str, List[str]], joiner: str = '\n', image_url: str = None,
                 image_alt_txt: str = ''):
        accessory = None
        if image_url is not None:
            accessory = ImageElement(image_url, image_alt_txt)
        super().__init__(text_elem=PlainTextElement(text=text, joiner=joiner), accessory=accessory)


class MarkdownSectionBlock(SectionBlock):
    def __init__(self, text: Union[str, List[str]], joiner: str = '\n', image_url: str = None,
                 image_alt_txt: str = ''):
        accessory = None
        if image_url is not None:
            accessory = ImageElement(image_url, image_alt_txt)
        super().__init__(text_elem=MarkdownTextElement(text=text, joiner=joiner), accessory=accessory)


class ButtonSectionBlock(SectionBlock):

    def __init__(self, text: Union[str, List[str]], button_text: str, value: str, action_id: str = 'button_action',
                 joiner: str = '\n'):
        accessory = ButtonElement(text=button_text, action_id=action_id, value=value)
        super().__init__(text_elem=MarkdownTextElement(text=text, joiner=joiner), accessory=accessory)


class StaticSelectSectionBlock(SectionBlock):

    def __init__(self, text: str, option_pairs: List[Tuple[str, str]], placeholder: str = None,
                 action_id: str = 'static-select', initial_option_pair: Tuple[str, str] = None):
        text_elem = PlainTextElement(text=text)
        placeholder_elem = None
        if placeholder is not None:
            placeholder_elem = PlainTextElement(text=placeholder)
        options = [OptionObject(text=PlainTextElement(txt), value=val) for txt, val in option_pairs]
        initial_option = None
        if initial_option_pair is not None:
            txt, val = initial_option_pair
            initial_option = OptionObject(text=PlainTextElement(txt), value=val)
        select_elem = StaticSelectElement(options=options, action_id=action_id, initial_option=initial_option,
                                          placeholder=placeholder_elem)
        super().__init__(
            text_elem=text_elem,
            accessory=select_elem
        )


class MultiStaticSelectSectionBlock(SectionBlock):

    def __init__(self, text: str, option_pairs: List[Tuple[str, str]], placeholder: str = None,
                 action_id: str = 'multi-static-select', initial_option_pairs: List[Tuple[str, str]] = None,
                 max_selected: int = None):
        text_elem = PlainTextElement(text=text)
        placeholder_elem = None
        if placeholder is not None:
            placeholder_elem = PlainTextElement(text=placeholder)
        options = [OptionObject(text=PlainTextElement(txt), value=val) for txt, val in option_pairs]
        initial_options = None
        if initial_option_pairs is not None:
            initial_options = [OptionObject(text=PlainTextElement(txt), value=val) for txt, val in initial_option_pairs]
        select_elem = MultiStaticSelectElement(options=options, action_id=action_id, initial_options=initial_options,
                                               placeholder=placeholder_elem, max_selected_items=max_selected)
        super().__init__(
            text_elem=text_elem,
            accessory=select_elem
        )


class UserSelectSectionBlock(SectionBlock):

    def __init__(self, text: str, placeholder: str = None, action_id: str = 'user-select', initial_user: str = None):
        text_elem = PlainTextElement(text=text)
        placeholder_elem = None
        if placeholder is not None:
            placeholder_elem = PlainTextElement(text=placeholder)
        select_elem = UserSelectElement(action_id=action_id, initial_user=initial_user,
                                        placeholder=placeholder_elem,)
        super().__init__(
            text_elem=text_elem,
            accessory=select_elem
        )


class MultiUserSelectSectionBlock(SectionBlock):

    def __init__(self, text: str, placeholder: str = None, action_id: str = 'multi-user-select',
                 initial_users: List[str] = None):
        text_elem = PlainTextElement(text=text)
        placeholder_elem = None
        if placeholder is not None:
            placeholder_elem = PlainTextElement(text=placeholder)
        select_elem = MultiUserSelectElement(action_id=action_id, initial_users=initial_users,
                                             placeholder=placeholder_elem)
        super().__init__(
            text_elem=text_elem,
            accessory=select_elem
        )
