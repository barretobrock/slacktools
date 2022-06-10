"""Block elements

References: https://api.slack.com/reference/block-kit/block-elements
"""
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    List,
    Union
)
import enum
from slacktools.block_kit.compositions import (
    ConfirmationDialogType,
    OptionType,
    OptionGroupType
)
from slacktools.block_kit.base import (
    BaseBlock,
    BaseElementType,
    PlainTextObjectType
)


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
    min_length: int
    max_length: int


class RadioButtonGroupType(BaseElementType):
    action_id: str
    options: List[OptionType]
    initial_option: OptionType
    confirm: ConfirmationDialogType


class SelectMenuElementType(enum.Enum):
    MULTI_STATIC = 'multi_static_select'
    MULTI_USER = 'multi_users_select'
    SINGLE_STATIC = 'static_select'
    SINGLE_USER = 'users_select'


class BlockElement(BaseBlock):

    @classmethod
    def make_button_element(cls, text: str, value: str, action_id: str, danger_style: bool = None,
                            confirm_obj: ConfirmationDialogType = None, url: str = None) -> ButtonElementType:
        """Builds a button element
        Args:
        """
        cls.perform_assertions({
            'text': (text, 75),
            'action_id': (action_id, 255),
            'value': (value, 2000),
            'url': (url, 3000)
        })
        btn_obj = {
            'type': 'button',
            'text': cls.plaintext_section(text=text),
            'value': value,
            'action_id': action_id
        }
        if danger_style is not None:
            btn_obj['style'] = 'danger' if danger_style else 'primary'
        if confirm_obj is not None:
            # Add in a confirm level
            btn_obj['confirm'] = confirm_obj
        if url is not None:
            btn_obj['url'] = url
        return btn_obj

    @classmethod
    def make_checkbox_element(cls, action_id: str, options: List[OptionType],
                              initial_options: List[OptionType] = None,
                              confirm_obj: ConfirmationDialogType = None) -> CheckboxElementType:
        cls.perform_assertions({
            'action_id': (action_id, 255),
            'options': (options, 10),
            'initial_options': (initial_options, 10),
        })
        ckbx_obj = {
            'type': 'checkboxes',
            'action_id': action_id,
            'options': options,

        }
        if initial_options is not None:
            ckbx_obj['initial_options'] = initial_options
        if confirm_obj is not None:
            ckbx_obj['confirm'] = confirm_obj
        return ckbx_obj

    @classmethod
    def make_datepicker_element(cls, action_id: str, placeholder: str = None,
                                initial_date: Union[str, datetime, date] = None,
                                confirm: ConfirmationDialogType = None) -> DatePickerElementType:
        cls.perform_assertions({
            'action_id': (action_id, 255),
            'placeholder': (placeholder, 150),
        })
        dtpick_obj = {
            'type': 'datepicker',
            'action_id': action_id
        }
        if placeholder is not None:
            dtpick_obj['placeholder'] = cls.plaintext_section(text=placeholder)
        if initial_date is not None:
            if isinstance(initial_date, str):
                initial_date = datetime.strptime(initial_date, '%Y-%m-%d').date()
            elif isinstance(initial_date, datetime):
                initial_date = initial_date.date()
            if isinstance(initial_date, date):
                dtpick_obj['initial_date'] = initial_date.strftime('%Y-%m-%d')
        if confirm is not None:
            dtpick_obj['confirm'] = confirm
        return dtpick_obj

    @classmethod
    def make_timepicker_element(cls, action_id: str, placeholder: str = None,
                                initial_time: Union[str, datetime, time] = None,
                                confirm: ConfirmationDialogType = None) -> TimePickerElementType:
        cls.perform_assertions({
            'action_id': (action_id, 255),
            'placeholder': (placeholder, 150),
        })
        tpick_obj = {
            'type': 'timepicker',
            'action_id': action_id
        }
        if placeholder is not None:
            tpick_obj['placeholder'] = cls.plaintext_section(text=placeholder)
        if initial_time is not None:
            if isinstance(initial_time, str):
                initial_time = datetime.strptime(initial_time, '%H:%M').time()
            elif isinstance(initial_time, datetime):
                initial_time = initial_time.time()
            if isinstance(initial_time, time):
                tpick_obj['initial_time'] = initial_time.strftime('%H:%M')
        if confirm is not None:
            tpick_obj['confirm'] = confirm
        return tpick_obj

    @classmethod
    def make_image_element(cls, url: str, alt_txt: str) -> ImageElementType:
        """Builds a dict for describing an accessory image, generally used with make_block_section
        Args:
            url: str, the url that points to the image
            alt_txt: str, alt text to the image. this will be displayed on hover / for any screen readers
        """
        return {
            'type': 'image',
            'image_url': url,
            'alt_text': alt_txt
        }

    @classmethod
    def _make_select_menu(cls, menu_type: SelectMenuElementType, placeholder: str, action_id: str,
                          confirm: ConfirmationDialogType = None,
                          max_selected_items: int = 1) -> \
            Union[MultiSelectStaticMenuType, MultiSelectUsersMenuType, StaticMenuType, UserMenuType]:
        """Handles building the structure of the multiselect menu that other methods depend on"""
        cls.perform_assertions({
            'placeholder': (placeholder, 150),
            'action_id': (action_id, 255),
        })
        ms_menu = {
            'type': menu_type.value,
            'placeholder': cls.plaintext_section(text=placeholder),
            'action_id': action_id,
        }
        if menu_type in [SelectMenuElementType.MULTI_STATIC, SelectMenuElementType.MULTI_USER]:
            ms_menu['max_selected_items'] = max_selected_items
        if confirm is not None:
            ms_menu['confirm'] = confirm
        return ms_menu

    @classmethod
    def make_static_menu(cls, placeholder: str, action_id: str, options: List[OptionType] = None,
                         option_groups: List[OptionGroupType] = None,
                         initial_option: List[Union[OptionType, OptionGroupType]] = None,
                         confirm: ConfirmationDialogType = None) -> \
            StaticMenuType:
        cls.perform_assertions({
            'options': (options, 100),
            'option_groups': (option_groups, 100)
        })
        # We can only use one of the two below, so at all times one must be empty while the other is not.
        if not ((options is not None) ^ (option_groups is not None)):
            raise ValueError('Only one option item can be populated! '
                             'Please set either the options or option_groups argument to None.')
        ms_menu = cls._make_select_menu(menu_type=SelectMenuElementType.SINGLE_STATIC, placeholder=placeholder,
                                        action_id=action_id, confirm=confirm)
        if options is not None:
            ms_menu['options'] = options
        elif option_groups is not None:
            ms_menu['option_groups'] = option_groups
        if initial_option is not None:
            ms_menu['initial_option'] = initial_option

        return ms_menu

    @classmethod
    def make_user_menu(cls, placeholder: str, action_id: str, initial_user: str = None,
                       confirm: ConfirmationDialogType = None) -> \
            UserMenuType:

        ms_menu = cls._make_select_menu(menu_type=SelectMenuElementType.SINGLE_USER, placeholder=placeholder,
                                        action_id=action_id, confirm=confirm)
        ms_menu: UserMenuType
        if initial_user is not None:
            ms_menu['initial_user'] = initial_user

        return ms_menu

    @classmethod
    def make_multiselect_static_menu(cls, placeholder: str, action_id: str, options: List[OptionType] = None,
                                     option_groups: List[OptionGroupType] = None,
                                     initial_options: List[Union[OptionType, OptionGroupType]] = None,
                                     confirm: ConfirmationDialogType = None, max_selected_items: int = 1) -> \
            MultiSelectStaticMenuType:
        cls.perform_assertions({
            'options': (options, 100),
            'option_groups': (option_groups, 100)
        })
        # We can only use one of the two below, so at all times one must be empty while the other is not.
        if not ((options is not None) ^ (option_groups is not None)):
            raise ValueError('Only one option item can be populated! '
                             'Please set either the options or option_groups argument to None.')
        ms_menu = cls._make_select_menu(menu_type=SelectMenuElementType.MULTI_STATIC, placeholder=placeholder,
                                        action_id=action_id, confirm=confirm,
                                        max_selected_items=max_selected_items)
        if options is not None:
            ms_menu['options'] = options
        elif option_groups is not None:
            ms_menu['option_groups'] = option_groups
        if initial_options is not None:
            ms_menu['initial_options'] = initial_options

        return ms_menu

    @classmethod
    def make_multiselect_user_menu(cls, placeholder: str, action_id: str,  initial_users: List[str] = None,
                                   confirm: ConfirmationDialogType = None, max_selected_items: int = 1) -> \
            MultiSelectUsersMenuType:

        ms_menu = cls._make_select_menu(menu_type=SelectMenuElementType.MULTI_USER, placeholder=placeholder,
                                        action_id=action_id, confirm=confirm,
                                        max_selected_items=max_selected_items)
        ms_menu: MultiSelectUsersMenuType
        if initial_users is not None:
            ms_menu['initial_users'] = initial_users

        return ms_menu

    @classmethod
    def make_overflow_menu(cls, action_id: str, options: List[OptionType],
                           confirm: ConfirmationDialogType = None) -> OverflowMenuType:
        cls.perform_assertions({
            'action_id': (action_id, 255),
            'options': (options, 5)
        })
        overflow_menu = {
            'type': 'overflow',
            'action_id': action_id,
            'options': options
        }
        if confirm is not None:
            overflow_menu['confirm'] = confirm
        return overflow_menu

    @classmethod
    def make_plaintext_input(cls, action_id: str, placeholder: str = None, initial_value: str = None,
                             multiline: bool = False, min_length: int = 0, max_length: int = 3000) -> \
            PlainTextInputType:
        cls.perform_assertions({
            'action_id': (action_id, 255),
            'placeholder': (placeholder, 150),
        })
        input_obj = {
            'type': 'plain_text_input',
            'action_id': action_id,
            'multiline': multiline,
            'min_length': min_length,
            'max_length': max_length
        }
        if placeholder is not None:
            input_obj['placeholder'] = cls.plaintext_section(text=placeholder)
        if initial_value is not None:
            input_obj['initial_value'] = initial_value

        return input_obj

    @classmethod
    def make_radio_button_group(cls, action_id: str, options: List[OptionType], initial_option: OptionType = None,
                                confirm: ConfirmationDialogType = None) -> \
            RadioButtonGroupType:
        cls.perform_assertions({
            'action_id': (action_id, 255),
            'options': (options, 10),
        })
        radio_obj = {
            'type': 'radio_buttons',
            'action_id': action_id,
            'options': options
        }
        if initial_option is not None:
            radio_obj['initial_option'] = initial_option
        if confirm is not None:
            radio_obj['confirm'] = confirm

        return radio_obj
