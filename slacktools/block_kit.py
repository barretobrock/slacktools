from typing import Union, List, Dict

class BlockKitBuilder:
    """Helper class to build out Block Kit things"""

    def __init__(self):
        pass

    @staticmethod
    def make_block_section(obj: Union[str, list], join_str: str = '\n', accessory: dict = None) -> dict:
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
            'text': {
                'type': 'mrkdwn',
                'text': txt
            }
        }

        if accessory is not None:
            section['accessory'] = accessory

        return section

    @staticmethod
    def make_image_accessory(url: str, alt_txt: str) -> dict:
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

    @staticmethod
    def make_block_divider() -> dict:
        """Returns a dict that renders a divider in Slack's Block Kit"""
        return {
            'type': 'divider'
        }

    @staticmethod
    def make_block_multiselect(desc: str, btn_txt: str, option_list: List[dict],
                               max_selected_items: int = None) -> dict:
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
                'text': {
                    'type': 'plain_text',
                    'text': x['txt'],
                    'emoji': True
                },
                'value': x['value']
            })

        multiselect_dict = {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': desc
            },
            'accessory': {
                'type': 'multi_static_select',
                'placeholder': {
                    'type': 'plain_text',
                    'text': btn_txt,
                    'emoji': True
                },
                'options': options
            }
        }

        if max_selected_items is not None:
            multiselect_dict['accessory']['max_selected_items'] = max_selected_items
        return multiselect_dict

    @staticmethod
    def make_block_button(btn_txt: str, value: str) -> dict:
        """Returns a dict that renders a button in Slack's Block Kit"""
        return {
            'type': 'button',
            'text': {
                'type': 'plain_text',
                'text': btn_txt,
                'emoji': True
            },
            'value': value
        }

    @staticmethod
    def make_context_section(txt_obj: Union[str, List[str]]) -> dict:
        """Takes in a list of text chunks and returns a dictionary
        that renders a context section in Block Kit
        Args:
            txt_obj: list of str or str, tex to include in the context block
        """
        if isinstance(txt_obj, str):
            element_list = [{'type': 'mrkdwn', 'text': txt_obj}]
        else:
            element_list = [{'type': 'mrkdwn', 'text': x} for x in txt_obj]

        return {
            "type": "context",
            "elements": element_list
        }

    def make_button_group(self, button_list: List[dict]) -> dict:
        """Takes in a list of dicts containing button text & value,
        returns a dictionary that renders the entire set of buttons together

        Args:
            button_list: list of dict, expected keys:
                txt: the button text
                value: the value attached to the button
        """
        return {
            'type': 'actions',
            'elements': [self.make_block_button(x['txt'], x['value']) for x in button_list]
        }

    @staticmethod
    def make_multi_user_select(label: str = 'Label', placeholder_txt: str = 'Select users') -> Dict:
        """Generates a multi-user select object"""
        return {
            'type': 'input',
            'element': {
                'type': 'multi_users_select',
                'placeholder': {
                    'type': 'plain_text',
                    'text': placeholder_txt,
                    'emoji': True
                },
                'action_id': 'multi_users_select-action'
            },
            'label': {
                'type': 'plain_text',
                'text': label,
                'emoji': True
            }
        }

    @staticmethod
    def make_radio_buttons(txt_obj: Union[str, List[str]], label: str = 'Label', name: str = 'radio-value') -> \
            Dict:
        """Generates a group of radio buttons"""
        if isinstance(txt_obj, str):
            option_list = [{'text': {'type': 'plain_text', 'text': txt_obj, 'emoji': True}, 'value': f'{name}-0'}]
        else:
            option_list = [{'text': {'type': 'plain_text', 'text': x, 'emoji': True},
                            'value': f'{name}-{i}'} for i, x in enumerate(txt_obj)]
        return {
            'type': 'input',
            'element': {
                'type': 'radio_buttons',
                'options': option_list,
                'action_id': 'radio_buttons-action'
            },
            'label': {
                'type': 'plain_text',
                'text': label,
                'emoji': True
            }
        }

    @staticmethod
    def make_header(txt: str) -> Dict:
        """Generates a header block"""
        return {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': txt,
                'emoji': True
            }
        }
