from typing import Union, List, Dict, Iterable


# Types
BaseDict = Dict[str, Union[str, bool]]
ListOfDicts = List[BaseDict]
NestedDict = Dict[str, BaseDict]
ListOfNestedDicts = List[NestedDict]
NestedBlock = Dict[str, Union[str, List[Iterable['NestedBlock']], Iterable['NestedBlock']]]


class BlockKitBase:
    """Base methods relied upon other, more complex ones down the line"""

    @classmethod
    def plaintext_section(cls, text: str) -> BaseDict:
        """Generates a plaintext area in a block"""
        return {
            'type': 'plain_text',
            'text': text,
            'emoji': True
        }

    @classmethod
    def markdown_section(cls, text: str) -> BaseDict:
        """Generates the generic text area in a block"""
        return {
            'type': 'mrkdwn',
            'text': text
        }

    @classmethod
    def make_block_divider(cls) -> BaseDict:
        """Returns a dict that renders a divider in Slack's Block Kit"""
        return {
            'type': 'divider'
        }

    @classmethod
    def make_image_accessory(cls, url: str, alt_txt: str) -> BaseDict:
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
    def build_accessory_section(cls, accessory_type: str, action_id: str = None, placeholder_txt: str = None,
                                url: str = None, text: str = None, image_url: str = None, alt_text: str = None,
                                value: str = None, options_list: ListOfNestedDicts = None) -> \
            Union[NestedDict, BaseDict]:
        """Makes an accessory section for a given element"""
        # Optional attributes that are added if their values aren't empty
        optionals = {
            'url': url,
            'action_id': action_id,
            'value': value,
            'placeholder': cls.plaintext_section(placeholder_txt) if placeholder_txt is not None else None,
            'text': cls.plaintext_section(text) if text is not None else None,
            'options': options_list,
            'image_url': image_url,
            'alt_text': alt_text,
        }
        accessory_dict = {
            'type': accessory_type
        }
        for k, v in optionals.items():
            if v is not None:
                accessory_dict[k] = v

        return accessory_dict

    @classmethod
    def build_link(cls, url: str, text: str) -> str:
        """Generates a link into slack's expected format"""
        return f'<{url}|{text}'

    @classmethod
    def make_confirm_object(cls, title: str = 'Are you sure?', text: str = 'Are you sure you want to do this?',
                            confirm_txt: str = 'Confirm', deny_txt: str = 'Cancel') \
            -> NestedDict:
        """Generates a confirmation object to be passed into the 'accessory' level of another UI object"""
        return {
            'title': cls.plaintext_section(title),
            'text': cls.markdown_section(text),
            'confirm': cls.plaintext_section(confirm_txt),
            'deny': cls.plaintext_section(deny_txt)
        }


class BlockKitText(BlockKitBase):
    """Block Kit methods for building out text objects"""

    @classmethod
    def make_header(cls, txt: str) -> NestedDict:
        """Generates a header block"""
        return {
            'type': 'header',
            'text': cls.plaintext_section(txt)
        }

    @classmethod
    def make_block_section(cls, obj: Union[str, list], join_str: str = '\n', accessory: BaseDict = None) ->\
            NestedDict:
        """Returns a Block Kit dictionary containing the markdown-supported text
        Args:
            obj: str or list, the block of text to include in the section
            join_str: str, the string to join a list of strings with
            accessory: dict, any acceptable acceccory to add to the section (e.g., button)
        """
        if isinstance(obj, list):
            txt = join_str.join(obj)
        elif isinstance(obj, str):
            txt = obj
        else:
            txt = str(obj)

        section = {
            'type': 'section',
            'text': cls.markdown_section(txt)
        }

        if accessory is not None:
            section['accessory'] = accessory

        return section

    @classmethod
    def make_text_section(cls, text: str, use_markdown: bool = False):
        """Generates a text section"""
        return {
            'type': 'section',
            'text': cls.plaintext_section(text) if not use_markdown else cls.markdown_section(text)
        }

    @classmethod
    def make_image_section_with_text(cls, text: str, image_url: str, alt_text: str) -> NestedDict:
        """Generates a text section with an image in it"""
        return {
            'type': 'section',
            'text': cls.plaintext_section(text),
            'accessory': cls.build_accessory_section(
                accessory_type='image', image_url=image_url, alt_text=alt_text
            )
        }

    @classmethod
    def make_text_fields(cls, text_list: List[str]) -> NestedBlock:
        """Generates text fields (array of texts that get positioned automatically in UI)"""
        return {
            'type': 'section',
            'fields': [cls.plaintext_section(x) for x in text_list]
        }

    @classmethod
    def make_context_section(cls, txt_obj: Union[str, List[str]]) -> Dict[str, Union[str, List[str]]]:
        """Takes in a list of text chunks and returns a dictionary
        that renders a context section in Block Kit
        Args:
            txt_obj: list of str or str, tex to include in the context block
        """
        if isinstance(txt_obj, str):
            element_list = [cls.markdown_section(txt_obj)]
        else:
            element_list = [cls.markdown_section(x) for x in txt_obj]

        return {
            "type": "context",
            "elements": element_list
        }


class BlockKitButtons(BlockKitBase):
    """Block Kit methods for building out buttons"""

    @classmethod
    def make_radio_buttons(cls, txt_obj: Union[str, List[str]], label: str = 'Label', name: str = 'radio-value',
                           action_id: str = 'radio_buttons-action') -> NestedBlock:
        """Generates a group of radio buttons"""
        if isinstance(txt_obj, str):
            option_list = [{'text': cls.plaintext_section(txt_obj), 'value': f'{name}-0'}]
        else:
            option_list = [{'text': cls.plaintext_section(x),
                            'value': f'{name}-{i}'} for i, x in enumerate(txt_obj)]
        return {
            'type': 'section',
            'text': cls.plaintext_section(label),
            'accessory': cls.build_accessory_section(accessory_type='radio_buttons', action_id=action_id,
                                                     options_list=option_list)
        }

    @classmethod
    def make_section_button(cls, label: str, url: str = None, btn_txt: str = 'Click Me',
                            value: str = 'btn_value_0', action_id: str = 'link-button-action') -> NestedDict:
        """Makes a button that takes up a section. When a link is included, it's opened on button click"""
        return {
            'type': 'section',
            'text': cls.markdown_section(label),
            'accessory': cls.build_accessory_section(accessory_type='button', text=btn_txt, value=value,
                                                     action_id=action_id, url=url)
        }

    @classmethod
    def make_action_button(cls, btn_txt: str, value: str, action_id: str) -> NestedBlock:
        """Returns a dict that renders an action button (standalone button) in Slack's Block Kit"""
        return {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': cls.plaintext_section(text=btn_txt),
                    'value': value,
                    'action_id': action_id
                }
            ]
        }

    @classmethod
    def make_action_button_group(cls, button_list: List[dict], action_id: str = 'action-button') -> \
            NestedBlock:
        """Takes in a list of dicts containing button text & value,
        returns a dictionary that renders the entire set of buttons together

        Args:
            button_list: list of dict, expected keys:
                txt: the button text
                value: the value attached to the button
            action_id
        """
        return {
            'type': 'actions',
            'elements': [cls.make_action_button(x['txt'], x['value'], action_id=f'{action_id}-{i}')
                         for i, x in enumerate(button_list)]
        }


class BlockKitSelect(BlockKitBase):
    """Block Kit methods for building out selection objects"""

    @classmethod
    def make_static_select(cls, label: str, option_list: ListOfDicts,
                           placeholder_txt: str = 'Select an item', action_id: str = 'static_select-action') -> \
            NestedDict:
        """Generates a single item selection dropdown
        Args:
            label: str, describes what is being selected
            placeholder_txt: str, text that goes over the dropdown box until a selection is made
            option_list: list of dict, options to include
                expected keys:
                    txt: option text
                    value: the value to apply to this option (returned in API)
            action_id: str, an id to attribute to this element
        """
        options_list = [{'text': cls.plaintext_section(x['txt']), 'value': x['value']} for x in option_list]

        return {
            'type': 'section',
            'text': cls.markdown_section(label),
            'accessory': cls.build_accessory_section(
                accessory_type='static_select', placeholder_txt=placeholder_txt, options_list=options_list,
                action_id=action_id
            )
        }

    @classmethod
    def make_user_select(cls, label: str, placeholder_txt: str = 'Select a user',
                         action_id: str = 'user_select-action') -> NestedDict:
        """Generates a single item user selection dropdown
        Args:
            label: str, describes what is being selected
            placeholder_txt: str, text that goes over the dropdown box until a selection is made
            action_id: str, an id to attribute to this element
        """

        return {
            'type': 'section',
            'text': cls.markdown_section(label),
            'accessory': cls.build_accessory_section(
                accessory_type='users_select', placeholder_txt=placeholder_txt, action_id=action_id
            )
        }

    @classmethod
    def make_multi_convo_select(cls, label: str, placeholder_txt: str = 'Select conversations',
                                action_id: str = 'mutli_conversation_select-action') -> NestedBlock:
        """Generates a multi-conversation
        Args:
            label: str, describes what is being selected
            placeholder_txt: str, text that goes over the dropdown box until a selection is made
            action_id: str, an id to attribute to this element
        """

        return {
            'type': 'section',
            'text': cls.markdown_section(label),
            'accessory': cls.build_accessory_section(
                accessory_type='multi_conversations_select', placeholder_txt=placeholder_txt, action_id=action_id
            )
        }

    @classmethod
    def make_block_multiselect(cls, desc: str, btn_txt: str, option_list: List[Dict[str, str]],
                               action_id: str = 'multi_users_select-action', max_selected_items: int = None)\
            -> Dict[str, Union[str, int, Dict]]:
        """Returns a dict that renders a multi select form in Slack's Block Kit
        Args:
            desc: str, the markdown-supported text that describes what's being selected
            btn_txt: str, text that goes inside the button element
            option_list: list of dict, options to include
                expected keys:
                    txt: option text
                    value: the value to apply to this option (returned in API)
            action_id:
            max_selected_items: int, if included, will establish a limit to the max number
                of selected items in the multiselect
        """

        options = []
        for x in option_list:
            options.append({
                'text': cls.plaintext_section(x['txt']),
                'value': x['value']
            })

        multiselect_dict = {
            'type': 'section',
            'text': cls.markdown_section(desc)
        }
        ms_accessory = {
            'type': 'multi_static_select',
            'placeholder': cls.plaintext_section(text=btn_txt),
            'options': options,
            'action_id': action_id
        }

        if max_selected_items is not None:
            ms_accessory.update({'max_selected_items': max_selected_items})
        multiselect_dict['accessory'] = ms_accessory
        return multiselect_dict

    @classmethod
    def make_multi_user_select(cls, label: str = 'Label', placeholder_txt: str = 'Select users',
                               initial_users: List[str] = None, action_id: str = 'multi_users_select-action',
                               confirm: Dict[str, Dict[str, str]] = None) -> \
            Dict[str, Union[str, Dict]]:
        """Generates a multi-user select object"""
        ms_accessory = {
                'type': 'multi_users_select',
                'placeholder': cls.plaintext_section(placeholder_txt),
                'action_id': action_id,
                'initial_users': [] if initial_users is None else initial_users
            }
        if confirm is not None:
            ms_accessory['confirm'] = confirm
        multi_user_select = {
            'type': 'section',
            'text': cls.markdown_section(label),
            'accessory': ms_accessory
        }
        return multi_user_select


class BlockKitDialog(BlockKitBase):
    @classmethod
    def make_dialog(cls, title: str, state: str, callback_id: str, elements_list: List[Dict],
                    submit_label: str = 'Submit') -> Dict[str, Union[str, Dict, List]]:
        """Generates a menu dialog"""
        return {
            'title': title,
            'callback_id': callback_id,
            'submit_label': submit_label,
            'state': state,
            'elements': elements_list
        }

    @classmethod
    def make_text_element(cls, label: str, name: str, subtype: str, placeholder: str) -> Dict[str, str]:
        """Makes a text element for dialogs"""
        return {
            'label': label,
            'name': name,
            'type': 'text',
            'subtype': subtype,
            'placeholder': placeholder
        }

    @classmethod
    def make_number_element(cls, label: str, name: str, placeholder: str):
        cls.make_text_element(label=label, name=name, placeholder=placeholder, subtype='number')

    @classmethod
    def make_email_element(cls, label: str, name: str, placeholder: str):
        cls.make_text_element(label=label, name=name, placeholder=placeholder, subtype='email')

    @classmethod
    def make_url_element(cls, label: str, name: str, placeholder: str):
        cls.make_text_element(label=label, name=name, placeholder=placeholder, subtype='url')

    @classmethod
    def make_textarea_element(cls, label: str, name: str, placeholder: str) -> Dict[str, str]:
        """Makes a textarea element for dialogs"""
        return {
            'label': label,
            'name': name,
            'type': 'textarea',
            'hint': placeholder
        }

    @classmethod
    def make_select_element(cls, label: str, name: str, options_list: List[Dict[str, str]] = None,
                            data_source: str = None, optional: bool = False) -> Dict[str, str]:
        """Makes a select element for dialogs
        Args:
            label:
            name:
            options_list:
                expected_keys:
                    label
                    value
            data_source:
            optional:
        """
        select_dict = {
            'label': label,
            'name': name,
            'type': 'select',
            'optional': optional
        }
        if data_source is not None:
            select_dict['data_source'] = data_source
        else:
            select_dict['options'] = options_list

        return select_dict


class BlockKitMenu(BlockKitBase):
    @classmethod
    def make_input_form(cls, title: str, submit_btn: str, input_objs: List[Dict[str, Dict]]) -> Dict:
        """Generates an input form"""
        return {
            'title': cls.plaintext_section(title),
            'submit': cls.plaintext_section(submit_btn),
            'type': 'modal',
            'blocks': input_objs
        }

    @classmethod
    def make_menu_option(cls, name: str, text: str, value: str, danger_style: bool = None, url: str = None,
                         incl_confirm: bool = False, confirm_title: str = None, confirm_text: str = None,
                         ok_text: str = None, dismiss_text: str = None) -> Dict[str, Union[str, Dict]]:
        """Generates a single menu button option
        """
        # TODO: Deprecate
        option = {
            'name': name,
            'text': text,
            'type': 'button',
            'value': value
        }
        if incl_confirm:
            # Add in a confirm level
            option['confirm'] = {
                'title': confirm_title,
                'text': confirm_text,
                'ok_text': ok_text,
                'dismiss_text': dismiss_text
            }
        if danger_style is not None:
            option['style'] = 'primary' if not danger_style else 'danger'
        if url is not None:
            option['url'] = url

        return option

    @classmethod
    def make_message_menu_attachment(cls, title: str, menu_options: List[Dict[str, str]],
                                     fallback: str, callback_id: str, color: str = '#3AA3E3') -> \
            List[Dict[str, Union[str, List, Dict]]]:
        """Generates a multi-button menu to be displayed inside a message
        NB! This should be passed in to the 'attachments' parameter in send_message
        """
        # TODO: Deprecate
        return [
            {
                'text': title,
                'fallback': fallback,
                'callback_id': callback_id,
                'color': color,
                'attachment_type': 'default',
                'actions': menu_options
            }
        ]


class BlockKitBuilder(BlockKitText, BlockKitButtons, BlockKitSelect, BlockKitMenu, BlockKitDialog):
    """Helper class to build out Block Kit things"""
    pass
