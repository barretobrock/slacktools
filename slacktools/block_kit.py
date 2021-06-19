from typing import Union, List, Dict


class BlockKitBase:
    """Base methods relied upon other, more complex ones down the line"""

    @classmethod
    def _plaintext_section(cls, text: str) -> Dict[str, Union[str, bool]]:
        """Generates a plaintext area in a block"""
        return {
            'type': 'plain_text',
            'text': text,
            'emoji': True
        }

    @classmethod
    def _markdown_section(cls, text: str) -> Dict[str, str]:
        """Generates the generic text area in a block"""
        return {
            'type': 'mrkdwn',
            'text': text
        }

    @classmethod
    def make_block_divider(cls) -> Dict[str, str]:
        """Returns a dict that renders a divider in Slack's Block Kit"""
        return {
            'type': 'divider'
        }

    @classmethod
    def make_image_accessory(cls, url: str, alt_txt: str) -> Dict[str, str]:
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


class BlockKitText(BlockKitBase):
    """Block Kit methods for building out text objects"""

    @classmethod
    def make_header(cls, txt: str) -> Dict:
        """Generates a header block"""
        return {
            'type': 'header',
            'text': cls._plaintext_section(txt)
        }

    @classmethod
    def make_block_section(cls, obj: Union[str, list], join_str: str = '\n', accessory: Dict[str, str] = None) ->\
            Dict[str, Union[str, Dict]]:
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
            'text': cls._markdown_section(txt)
        }

        if accessory is not None:
            section['accessory'] = accessory

        return section

    @classmethod
    def make_context_section(cls, txt_obj: Union[str, List[str]]) -> Dict[str, Union[str, List[str]]]:
        """Takes in a list of text chunks and returns a dictionary
        that renders a context section in Block Kit
        Args:
            txt_obj: list of str or str, tex to include in the context block
        """
        if isinstance(txt_obj, str):
            element_list = [cls._markdown_section(txt_obj)]
        else:
            element_list = [cls._markdown_section(x) for x in txt_obj]

        return {
            "type": "context",
            "elements": element_list
        }


class BlockKitButtons(BlockKitBase):
    """Block Kit methods for building out buttons"""

    @classmethod
    def make_radio_buttons(cls, txt_obj: Union[str, List[str]], label: str = 'Label',
                           name: str = 'radio-value') -> Dict:
        """Generates a group of radio buttons"""
        if isinstance(txt_obj, str):
            option_list = [{'text': cls._plaintext_section(txt_obj), 'value': f'{name}-0'}]
        else:
            option_list = [{'text': cls._plaintext_section(x),
                            'value': f'{name}-{i}'} for i, x in enumerate(txt_obj)]
        return {
            'type': 'input',
            'element': {
                'type': 'radio_buttons',
                'options': option_list,
                'action_id': 'radio_buttons-action'
            },
            'label': cls._plaintext_section(label)
        }

    @classmethod
    def make_link_button(cls, label: str, url: str, btn_txt: str = 'Click Me', value: str = 'btn_value_0') -> \
            Dict[str, Union[str, Dict]]:
        """Makes a link rendered as a button"""
        return {
            'type': 'section',
            'text': cls._markdown_section(label),
            'accessory': {
                'type': 'button',
                'text': cls._plaintext_section(btn_txt),
                'value': value,
                'url': url,
                'action_id': 'link-button-action'
            }
        }

    @classmethod
    def make_block_button(cls, btn_txt: str, value: str) -> Dict[str, str]:
        """Returns a dict that renders a block button (button in a section) in Slack's Block Kit"""
        return {
            'type': 'button',
            'text': cls._plaintext_section(text=btn_txt),
            'value': value
        }

    @classmethod
    def make_block_button_group(cls, button_list: List[dict]) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Takes in a list of dicts containing button text & value,
        returns a dictionary that renders the entire set of buttons together

        Args:
            button_list: list of dict, expected keys:
                txt: the button text
                value: the value attached to the button
        """
        return {
            'type': 'actions',
            'elements': [cls.make_block_button(x['txt'], x['value']) for x in button_list]
        }

    @classmethod
    def make_action_button(cls, btn_txt: str, value: str, action_id: str) -> Dict[str, Union[str, List[Dict]]]:
        """Returns a dict that renders an action button (standalone button) in Slack's Block Kit"""
        return {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': cls._plaintext_section(text=btn_txt),
                    'value': value,
                    'action_id': action_id
                }
            ]
        }

    @classmethod
    def make_action_button_group(cls, button_list: List[dict]) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Takes in a list of dicts containing button text & value,
        returns a dictionary that renders the entire set of buttons together

        Args:
            button_list: list of dict, expected keys:
                txt: the button text
                value: the value attached to the button
        """
        return {
            'type': 'actions',
            'elements': [cls.make_action_button(x['txt'], x['value'], action_id=f'action-button-{i}')
                         for i, x in enumerate(button_list)]
        }


class BlockKitSelect(BlockKitBase):
    """Block Kit methods for building out selection objects"""

    @classmethod
    def make_static_select(cls, label: str, option_list: List[Dict[str, str]],
                           placeholder_txt: str = 'Select an item') -> Dict[str, Union[str, Dict]]:
        """Generates a single item selection dropdown
        Args:
            label: str, describes what is being selected
            placeholder_txt: str, text that goes over the dropdown box until a selection is made
            option_list: list of dict, options to include
                expected keys:
                    txt: option text
                    value: the value to apply to this option (returned in API)
        """
        return {
            'type': 'section',
            'text': cls._markdown_section(label),
            'accessory': {
                'type': 'static_select',
                'placeholder': cls._plaintext_section(placeholder_txt),
                'options': [
                    {'text': cls._plaintext_section(x['txt']), 'value': x['value']} for x in option_list
                ],
                'action_id': 'static_select-action'
            }
        }

    @classmethod
    def make_block_multiselect(cls, desc: str, btn_txt: str, option_list: List[Dict[str, str]],
                               max_selected_items: int = None) -> Dict[str, Union[str, int, Dict]]:
        """Returns a dict that renders a multi select form in Slack's Block Kit
        Args:
            desc: str, the markdown-supported text that describes what's being selected
            btn_txt: str, text that goes inside the button element
            option_list: list of dict, options to include
                expected keys:
                    txt: option text
                    value: the value to apply to this option (returned in API)
            max_selected_items: int, if included, will establish a limit to the max number
                of selected items in the multiselect
        """

        options = []
        for x in option_list:
            options.append({
                'text': cls._plaintext_section(x['txt']),
                'value': x['value']
            })

        multiselect_dict = {
            'type': 'section',
            'text': cls._markdown_section(desc)
        }
        ms_accessory = {
            'type': 'multi_static_select',
            'placeholder': cls._plaintext_section(text=btn_txt),
            'options': options
        }

        if max_selected_items is not None:
            ms_accessory.update({'max_selected_items': max_selected_items})
        multiselect_dict['accessory'] = ms_accessory
        return multiselect_dict

    @classmethod
    def make_multi_user_select(cls, label: str = 'Label', placeholder_txt: str = 'Select users') -> \
            Dict[str, Union[str, Dict]]:
        """Generates a multi-user select object"""
        return {
            'type': 'input',
            'element': {
                'type': 'multi_users_select',
                'placeholder': cls._plaintext_section(placeholder_txt),
                'action_id': 'multi_users_select-action'
            },
            'label': cls._plaintext_section(label)
        }


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
                            data_source: str = None) -> Dict[str, str]:
        """Makes a select element for dialogs
        Args:
            label:
            name:
            options_list:
                expected_keys:
                    label
                    value
            data_source:
        """
        select_dict = {
            'label': label,
            'name': name,
            'type': 'select'
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
            'title': cls._plaintext_section(title),
            'submit': cls._plaintext_section(submit_btn),
            'type': 'modal',
            'blocks': input_objs
        }

    @classmethod
    def make_menu_option(cls, name: str, text: str, value: str, incl_confirm: bool = False,
                         confirm_title: str = None, confirm_text: str = None, ok_text: str = None,
                         dismiss_text: str = None) -> Dict[str, Union[str, Dict]]:
        """Generates a single menu button option
        """
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

        return option

    @classmethod
    def make_message_menu_attachment(cls, title: str, menu_options: List[Dict[str, str]],
                                     fallback: str, callback_id: str, color: str = '#3AA3E3') -> \
            List[Dict[str, Union[str, List, Dict]]]:
        """Generates a multi-button menu to be displayed inside a message
        NB! This should be passed in to the 'attachments' parameter in send_message
        """
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
