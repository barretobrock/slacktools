import re
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)


def nested_dict_field_extractor_replacer(d: Dict, num: int = 0, placeholders: Dict[str, str] = None,
                                         extract: bool = True) -> Tuple[Dict, Dict, int]:
    """Iterates through a nested dict, replaces items in 'text' field with placeholders and vice versa
    Args:
        d: dict, the (likely nested) input dictionary to work on
        num: int, the nth placeholder we're working on
        placeholders: dict,
            key = placeholder text,
            value = original text if extract == True otherwise translated
        extract: bool, if True, will extract from d -> placeholders
            if False, will replace placeholder text in d with translated text in placeholders
    """
    if placeholders is None:
        placeholders = {}

    for k, v in d.copy().items():
        if isinstance(v, dict):
            placeholders, d[k], num = nested_dict_field_extractor_replacer(v, num, placeholders, extract=extract)
        elif isinstance(v, list):
            for j, item in enumerate(v):
                placeholders, d[k][j], num = nested_dict_field_extractor_replacer(item, num, placeholders,
                                                                                  extract=extract)
        else:
            if k == 'text':
                if extract:
                    placeholder = f'placeholder_{num}'
                    # Take the text and move it to the temp dict
                    placeholders[placeholder] = v
                    # Replace the value in the real dict with the placeholder
                    d[k] = placeholder
                    num += 1
                else:
                    # Replace placeholder text with translated text
                    placeholder = d[k]
                    d[k] = placeholders[placeholder]
    return placeholders, d, num


def block_text_converter(blocks: List[dict], callable_list: list) -> List[dict]:
    """
    Process:
        1. Iterates through a block, grabs text from target fields, replaces it with 'placeholder_x',
            where x is the nth replacement
        2. Take the dictionary of text with placeholders, applies a function to every text to
            process it in to something else, then replacing the text in that dictionary with the modified text
        3. Takes the dictionary with the replaced text and applies it back into the block
    """
    translations_dict = {}
    for block in blocks:
        txt_dict, block_dict, n = nested_dict_field_extractor_replacer(block)
        if len(txt_dict) > 0:
            for k, v in txt_dict.items():
                if 'text' in callable_list:
                    # Duplicate the list to avoid the original being overwritten
                    clist = callable_list.copy()
                    # Swap this string out for the actual text
                    txt_pos = clist.index('text')
                    clist[txt_pos] = v
                    translations_dict[k] = clist[0](*clist[1:])
                else:
                    translations_dict[k] = callable_list[0](*callable_list[1:])

    # Replace blocks with translations
    for i, block in enumerate(blocks):
        txt_dict, block_dict, n = nested_dict_field_extractor_replacer(block, placeholders=translations_dict,
                                                                       extract=False)
        blocks[i] = block_dict

    return blocks


class SlackInputParser:
    """A class solely meant to help parse input from Slack into usable data"""

    @staticmethod
    def parse_tag_from_text(txt: str) -> Optional[str]:
        """Parses an <@{user}> mention and extracts the user id from it"""
        match = re.match(r'^<@(.*)>', txt)
        if match is not None:
            # IDs are stored as uppercase. This will help with matching
            return match.group(1).upper()
        return None

    @classmethod
    def parse_flags_from_command(cls, message: str) -> Dict[str, str]:
        """Takes in a message string and parses out flags in the string and the values following them
        Args:
            message: str, the command message containing the flags

        Returns:
            dict, flags parsed out into keys

        Example:
            >>> msg = 'process this command -l -u this that other --p 1 2 3 4 5'
            >>> #parse_flags_from_command(msg)
            >>> {
            >>>     'cmd': 'process this command',
            >>>     'l': '',
            >>>     'u': 'this that other',
            >>>     'p': '1 2 3 4 5'
            >>> }
        """
        msg_split = message.split(' ')
        cmd_dict = {
            'cmd': re.split(r'-+\w+', message)[0].strip()
        }
        flag_regex = re.compile(r'^-+(\w+)')
        for i, part in enumerate(msg_split):
            if flag_regex.match(part) is not None:
                flag = flag_regex.match(part).group(1)
                # Get list of values after the flag up until the next flag
                vals = []
                for val in msg_split[i + 1:]:
                    if flag_regex.match(val) is not None:
                        break
                    vals.append(val)
                cmd_dict[flag] = ' '.join(vals)
        return cmd_dict

    @classmethod
    def get_flag_from_command(cls, cmd: str, flags: Union[str, List[str]], default: Optional[str] = None) -> str:
        """Reads in the command, if no flag, will return the default
        Args:
            cmd: str, the command message to parse
            flags: str or list of str, the flag(s) to search for
            default: str, the default value to set if no flag is found
        """

        # Parse the command into a dictionary of the command parts (command, flags)
        parsed_cmd = cls.parse_flags_from_command(cmd)
        if isinstance(flags, str):
            # Put this into a list to unify our examination methods
            flags = [flags]

        for flag in flags:
            if flag in parsed_cmd.keys():
                return parsed_cmd[flag]
        return default
