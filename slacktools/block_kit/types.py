from typing import (
    List,
    TypedDict,
    Union,
)


class BaseElementType(TypedDict):
    type: str


class PlainTextObjectType(BaseElementType):
    text: str
    emoji: bool


class MarkdownTextObjectType(PlainTextObjectType):
    verbatim: bool


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


class DispatchActionType(TypedDict):
    trigger_actions_on: List[str]


class ButtonElementType(BaseElementType, total=False):
    text: PlainTextObjectType
    value: str
    action_id: str
    style: str
    confirm: ConfirmationDialogType
    url: str


class CheckboxElementType(BaseElementType, total=False):
    action_id: str
    options: List[OptionType]
    initial_options: List[OptionType]
    confirm: ConfirmationDialogType


class DatePickerElementType(BaseElementType, total=False):
    action_id: str
    placeholder: PlainTextObjectType
    initial_date: str
    confirm: ConfirmationDialogType


class TimePickerElementType(BaseElementType, total=False):
    action_id: str
    placeholder: PlainTextObjectType
    initial_time: str
    confirm: ConfirmationDialogType


class ImageElementType(BaseElementType, total=False):
    image_url: str
    alt_text: str


class SelectBaseMenuType(BaseElementType, total=False):
    placeholder: PlainTextObjectType
    action_id: str
    confirm: ConfirmationDialogType


class StaticMenuType(SelectBaseMenuType, total=False):
    options: List[OptionType]
    option_groups: List[OptionGroupType]
    initial_option: Union[OptionType, OptionGroupType]


class UserMenuType(SelectBaseMenuType, total=False):
    initial_user: str


class MultiSelectBaseMenuType(SelectBaseMenuType, total=False):
    max_selected_items: int


class MultiSelectStaticMenuType(MultiSelectBaseMenuType, total=False):
    options: List[OptionType]
    option_groups: List[OptionGroupType]
    initial_options: List[Union[OptionType, OptionGroupType]]


class MultiSelectUsersMenuType(MultiSelectBaseMenuType, total=False):
    initial_users: List[str]


class OverflowMenuType(BaseElementType):
    action_id: str
    options: List[OptionType]
    confirm: ConfirmationDialogType


class PlainTextInputType(BaseElementType):
    action_id: str
    placeholder: PlainTextObjectType
    initial_value: str
    multiline: bool
    dispatch_action_config: DispatchActionType
    min_length: int
    max_length: int


class RadioButtonGroupType(BaseElementType):
    action_id: str
    options: List[OptionType]
    initial_option: OptionType
    confirm: ConfirmationDialogType


ElementObjects = Union[ButtonElementType, MultiSelectStaticMenuType, UserMenuType, StaticMenuType,
                       MultiSelectUsersMenuType, OverflowMenuType, DatePickerElementType, TimePickerElementType]

InputBlockElements = Union[PlainTextInputType, MultiSelectUsersMenuType, MultiSelectStaticMenuType,
                           StaticMenuType, UserMenuType, CheckboxElementType, RadioButtonGroupType,
                           DatePickerElementType, TimePickerElementType]

AccessoryBlockElements = Union[ButtonElementType, CheckboxElementType, DatePickerElementType, ImageElementType,
                               MultiSelectStaticMenuType, MultiSelectUsersMenuType, OverflowMenuType,
                               PlainTextInputType, RadioButtonGroupType, UserMenuType, StaticMenuType,
                               TimePickerElementType]

TextObjects = Union[PlainTextObjectType, MarkdownTextObjectType]


class ActionsBlockType(BaseElementType, total=False):
    elements: List[ElementObjects]
    block_id: str


class ContextBlockType(BaseElementType, total=False):
    elements: List[Union[TextObjects, ImageElementType]]
    block_id: str


class DividerType(BaseElementType, total=False):
    block_id: str


class HeaderBlockType(BaseElementType, total=False):
    text: PlainTextObjectType
    block_id: str


class ImageBlockType(BaseElementType, total=False):
    image_url: str
    alt_text: str
    title: PlainTextObjectType
    block_id: str


class InputBlockType(BaseElementType, total=False):
    dispatch_action: bool
    label: PlainTextObjectType
    element: InputBlockElements
    block_id: str
    hint: PlainTextObjectType
    optional: bool


class SectionBlockType(BaseElementType, total=False):
    text: TextObjects
    block_id: str
    fields: List[TextObjects]
    accessory: AccessoryBlockElements
