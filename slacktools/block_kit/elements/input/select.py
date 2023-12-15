from typing import (
    List,
    Union,
)

from slacktools.block_kit.base import BaseElement
from slacktools.block_kit.elements.display.text import PlainTextElement
from slacktools.block_kit.elements.input.button import ConfirmElement


class OptionObject(BaseElement):
    text: PlainTextElement
    value: str
    description: PlainTextElement
    url: str

    def __init__(self, text: PlainTextElement, value: str, description: PlainTextElement = None, url: str = None):
        self.text = text
        self.value = value
        if description is not None:
            self.description = description
            self.length_assertion(self.description.text, 'desc_text', 75)
        if url is not None:
            self.url = url
        super().__init__()
        self.length_assertion(self.text.text, 'text_text', 75)
        self.length_assertion(self.value, 'value', 75)


class OptionGroupObject(BaseElement):
    label: PlainTextElement
    options: List[OptionObject]

    def __init__(self, label: PlainTextElement, options: List[OptionObject]):
        self.label = label
        self.options = options
        super().__init__()
        self.length_assertion(self.label.text, 'label_text', 75)
        self.length_assertion(self.options, 'options', 100)


class StaticSelectElement(BaseElement):
    """
    https://api.slack.com/reference/block-kit/block-elements#select
    """
    type: str = 'static_select'
    action_id: str
    options: List[OptionObject]
    option_groups: List[OptionGroupObject]
    initial_option: Union[OptionObject, OptionGroupObject]
    confirm: ConfirmElement
    focus_on_load: bool = False
    placeholder: PlainTextElement

    def __init__(self, options: List[OptionObject] = None, option_groups: List[OptionGroupObject] = None,
                 action_id: str = 'static-select', initial_option: OptionObject = None, confirm: ConfirmElement = None,
                 focus_on_load: bool = False, placeholder: PlainTextElement = None):
        if options is None and option_groups is None:
            raise ValueError('One of options or option_group must be populated.')
        if options is not None:
            self.options = options
            self.length_assertion(self.options, 'options', 100)
        elif option_groups is not None:
            self.option_groups = option_groups
            self.length_assertion(self.option_groups, 'option_groups', 100)

        if initial_option is not None:
            self.initial_option = initial_option
        if confirm is not None:
            self.confirm = confirm
        if placeholder is not None:
            self.placeholder = placeholder
        self.action_id = action_id
        self.length_assertion(self.action_id, 'action_id', 255)
        self.focus_on_load = focus_on_load
        super().__init__(type=self.type)


class MultiStaticSelectElement(BaseElement):
    """
    https://api.slack.com/reference/block-kit/block-elements#static_multi_select
    """
    type: str = 'multi_static_select'
    action_id: str
    options: List[OptionObject]
    option_groups: List[OptionGroupObject]
    initial_options: List[Union[OptionObject, OptionGroupObject]]
    confirm: ConfirmElement
    max_selected_items: int
    focus_on_load: bool = False
    placeholder: PlainTextElement

    def __init__(self, options: List[OptionObject] = None, option_groups: List[OptionGroupObject] = None,
                 action_id: str = 'static-select', initial_options: List[OptionObject] = None,
                 confirm: ConfirmElement = None, max_selected_items: int = None, focus_on_load: bool = False,
                 placeholder: PlainTextElement = None):
        if options is None and option_groups is None:
            raise ValueError('One of options or option_group must be populated.')
        if options is not None:
            self.options = options
            self.length_assertion(self.options, 'options', 100)
        elif option_groups is not None:
            self.option_groups = option_groups
            self.length_assertion(self.option_groups, 'option_groups', 100)

        if initial_options is not None:
            self.initial_options = initial_options
        if confirm is not None:
            self.confirm = confirm
        if placeholder is not None:
            self.placeholder = placeholder
        if max_selected_items is not None:
            self.max_selected_items = max_selected_items
        self.action_id = action_id
        self.length_assertion(self.action_id, 'action_id', 255)
        self.focus_on_load = focus_on_load
        super().__init__(type=self.type)


class UserSelectElement(BaseElement):
    """
    https://api.slack.com/reference/block-kit/block-elements#users_select
    """
    type: str = 'users_select'
    action_id: str
    initial_user: str
    confirm: ConfirmElement
    focus_on_load: bool = False
    placeholder: PlainTextElement

    def __init__(self, action_id: str = 'user-select', initial_user: str = None, confirm: ConfirmElement = None,
                 focus_on_load: bool = False, placeholder: PlainTextElement = None):

        if initial_user is not None:
            self.initial_user = initial_user
        if confirm is not None:
            self.confirm = confirm
        if placeholder is not None:
            self.placeholder = placeholder
        self.action_id = action_id
        self.length_assertion(self.action_id, 'action_id', 255)
        self.focus_on_load = focus_on_load
        super().__init__(type=self.type)


class MultiUserSelectElement(BaseElement):
    """
    https://api.slack.com/reference/block-kit/block-elements#users_select
    """
    type: str = 'multi_users_select'
    action_id: str
    initial_users: List[str]
    confirm: ConfirmElement
    max_selected_items: int
    focus_on_load: bool = False
    placeholder: PlainTextElement

    def __init__(self, action_id: str = 'multi-user-select', initial_users: List[str] = None,
                 max_selected_items: int = None, confirm: ConfirmElement = None, focus_on_load: bool = False,
                 placeholder: PlainTextElement = None):

        if initial_users is not None:
            self.initial_users = initial_users
        if confirm is not None:
            self.confirm = confirm
        if placeholder is not None:
            self.placeholder = placeholder
            self.length_assertion(self.placeholder.text, 'placeholder.text', 150)
        if max_selected_items is not None:
            self.max_selected_items = max_selected_items
        self.action_id = action_id
        self.length_assertion(self.action_id, 'action_id', 255)
        self.focus_on_load = focus_on_load
        super().__init__(type=self.type)
