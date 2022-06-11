from typing import (
    List,
    Union
)
from slacktools.block_kit.base import BaseBlock
from slacktools.block_kit.types import (
    AccessoryBlockElements,
    ActionsBlockType,
    ConfirmationDialogType,
    ContextBlockType,
    DispatchActionType,
    DividerType,
    ElementObjects,
    HeaderBlockType,
    ImageBlockType,
    ImageElementType,
    InputBlockElements,
    InputBlockType,
    OptionType,
    OptionGroupType,
    SectionBlockType,
    TextObjects
)
from slacktools.block_kit.elements import BlockElement


class LayoutBlock(BaseBlock):
    """https://api.slack.com/reference/block-kit/blocks"""

    @classmethod
    def make_actions_block(cls, elements: List[ElementObjects], block_id: str = None) -> ActionsBlockType:
        cls.perform_assertions({
            'elements': (elements, 25),
            'block_id': (block_id, 255)
        })
        actions = {
            'type': 'actions',
            'elements': elements
        }
        if block_id is not None:
            actions['block_id'] = block_id
        return actions

    @classmethod
    def make_context_block(cls, elements: List[Union[ImageElementType, TextObjects]], block_id: str = None) -> \
            ContextBlockType:
        cls.perform_assertions({
            'elements': (elements, 10),
            'block_id': (block_id, 255)
        })
        actions = {
            'type': 'context',
            'elements': elements
        }
        if block_id is not None:
            actions['block_id'] = block_id
        return actions

    @classmethod
    def make_divider_block(cls, block_id: str = None) -> DividerType:
        """Returns a dict that renders a divider in Slack's Block Kit
        Docs: https://api.slack.com/reference/block-kit/blocks#divider
        """
        cls.perform_assertions({
            'block_id': (block_id, 255)
        })
        div = {
            'type': 'divider'
        }
        if block_id is not None:
            div['block_id'] = block_id
        return div

    @classmethod
    def make_header_block(cls, text: str, block_id: str = None) -> HeaderBlockType:
        cls.perform_assertions({
            'text': (text, 150),
            'block_id': (block_id, 255)
        })
        header = {
            'type': 'header',
            'text': cls.plaintext_section(text=text)
        }
        if block_id is not None:
            header['block_id'] = block_id
        return header

    @classmethod
    def make_image_block(cls, image_url: str, alt_text: str = 'Image', title: str = None,
                         block_id: str = None) -> ImageBlockType:
        cls.perform_assertions({
            'image_url': (image_url, 3000),
            'alt_text': (alt_text, 2000),
            'title': (title, 2000),
            'block_id': (block_id, 255)
        })
        image = {
            'type': 'image',
            'image_url': image_url,
            'alt_text': alt_text,
            'title': cls.plaintext_section(text=title)
        }
        if block_id is not None:
            image['block_id'] = block_id
        return image

    @classmethod
    def make_input_block(cls, label: str, element: InputBlockElements, block_id: str = None, hint: str = None,
                         optional: bool = False, dispatch_action: bool = None) -> InputBlockType:
        cls.perform_assertions({
            'label': (label, 2000),
            'block_id': (block_id, 255),
            'hint': (hint, 2000)
        })
        input_blk = {
            'type': 'input',
            'label': cls.plaintext_section(text=label),
            'element': element,
            'optional': optional
        }
        if block_id is not None:
            input_blk['block_id'] = block_id
        if hint is not None:
            input_blk['hint'] = cls.plaintext_section(text=hint)
        if dispatch_action is not None:
            input_blk['dispatch_action'] = dispatch_action
        return input_blk

    @classmethod
    def make_section_block(cls, text_obj: TextObjects = None, block_id: str = None,
                           fields: List[TextObjects] = None, accessory: AccessoryBlockElements = None) -> \
            SectionBlockType:
        cls.perform_assertions({
            'block_id': (block_id, 255),
            'fields': (fields, 10)
        })
        section = {
            'type': 'section'
        }
        if text_obj is not None:
            section['text'] = text_obj
        if block_id is not None:
            section['block_id'] = block_id
        if fields is not None and text_obj is None:
            section['fields'] = fields
        if accessory is not None:
            section['accessory'] = accessory
        return section

    @classmethod
    def make_section_with_button(cls, label: str, block_id: str = None, btn_txt: str = 'Click Me',
                                 value: str = 'btn-value-0', action_id: str = 'button-action',
                                 danger_style: bool = None, confirm_obj: ConfirmationDialogType = None,
                                 url: str = None) -> SectionBlockType:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return cls.make_section_block(
            text_obj=cls.plaintext_section(text=label),
            block_id=block_id,
            accessory=BlockElement.make_button_element(
                text=btn_txt,
                value=value,
                action_id=action_id,
                danger_style=danger_style,
                confirm_obj=confirm_obj,
                url=url
            )
        )

    @classmethod
    def make_section_with_radio_buttons(cls, label: str, options: List[OptionType], initial_option: OptionType,
                                        block_id: str = None, action_id: str = 'radio-button-action',
                                        confirm_obj: ConfirmationDialogType = None) -> SectionBlockType:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return cls.make_section_block(
            text_obj=cls.plaintext_section(text=label),
            block_id=block_id,
            accessory=BlockElement.make_radio_button_group(
                action_id=action_id,
                options=options,
                initial_option=initial_option,
                confirm=confirm_obj,
            )
        )

    @classmethod
    def make_section_with_static_select(cls, label: str, options: List[Union[OptionType, OptionGroupType]],
                                        initial_option: Union[OptionType, OptionGroupType],
                                        placeholder: str = None,
                                        block_id: str = None, action_id: str = 'static-select-action',
                                        confirm_obj: ConfirmationDialogType = None) -> SectionBlockType:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return cls.make_section_block(
            text_obj=cls.plaintext_section(text=label),
            block_id=block_id,
            accessory=BlockElement.make_static_menu(
                action_id=action_id,
                placeholder=placeholder,
                options=options,
                initial_option=initial_option,
                confirm=confirm_obj,
            )
        )

    @classmethod
    def make_section_with_multistatic_select(cls, label: str, options: List[Union[OptionType, OptionGroupType]],
                                             initial_options: List[Union[OptionType, OptionGroupType]],
                                             placeholder: str = None, block_id: str = None,
                                             action_id: str = 'multistatic-select-action',
                                             confirm_obj: ConfirmationDialogType = None,
                                             max_items: int = None) -> SectionBlockType:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return cls.make_section_block(
            text_obj=cls.plaintext_section(text=label),
            block_id=block_id,
            accessory=BlockElement.make_multiselect_static_menu(
                action_id=action_id,
                placeholder=placeholder,
                options=options,
                initial_options=initial_options,
                confirm=confirm_obj,
                max_selected_items=max_items
            )
        )

    @classmethod
    def make_section_with_user_select(cls, label: str, initial_user: str = None,
                                      placeholder: str = 'Select a user', block_id: str = None,
                                      action_id: str = 'select-user-action',
                                      confirm_obj: ConfirmationDialogType = None) -> SectionBlockType:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return cls.make_section_block(
            text_obj=cls.plaintext_section(text=label),
            block_id=block_id,
            accessory=BlockElement.make_user_menu(
                action_id=action_id,
                placeholder=placeholder,
                initial_user=initial_user,
                confirm=confirm_obj
            )
        )

    @classmethod
    def make_section_with_multiuser_select(cls, label: str, initial_users: List[str] = None,
                                           placeholder: str = 'Select user(s)', block_id: str = None,
                                           action_id: str = 'multi-select-users-action',
                                           confirm_obj: ConfirmationDialogType = None, max_users: int = None) -> \
            SectionBlockType:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return cls.make_section_block(
            text_obj=cls.plaintext_section(text=label),
            block_id=block_id,
            accessory=BlockElement.make_multiselect_user_menu(
                action_id=action_id,
                placeholder=placeholder,
                initial_users=initial_users,
                confirm=confirm_obj,
                max_selected_items=max_users
            )
        )

    @classmethod
    def make_section_with_plaintext_input(cls, label: str, action_id: str = 'plain-text-input',
                                          block_id: str = None, hint: str = None, optional: bool = None,
                                          placeholder: str = None, initial_value: str = None,
                                          multiline: bool = False, min_length: int = 0, max_length: int = 3000,
                                          dispatch_actions: DispatchActionType = None) -> InputBlockType:
        return cls.make_input_block(
            label=label,
            dispatch_action=True,
            element=BlockElement.make_plaintext_input(
                action_id=action_id,
                placeholder=placeholder,
                initial_value=initial_value,
                multiline=multiline,
                min_length=min_length,
                max_length=max_length,
                dispatch_actions=dispatch_actions
            ),
            block_id=block_id,
            hint=hint,
            optional=optional
        )
