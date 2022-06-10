from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Dict,
    List,
    Tuple,
    TypedDict,
    Union
)
import enum


class BaseElementType(TypedDict):
    type: str


class PlainTextObjectType(BaseElementType):
    text: str
    emoji: bool


class MarkdownTextObjectType(PlainTextObjectType):
    verbatim: bool


class StringExceededMaxLengthException(Exception):
    pass


class DateFormatType(enum.Enum):
    date_num = enum.auto()  # %Y-%m-%d
    date = enum.auto()           # %B %d, %Y
    date_short = enum.auto()  # %B %d, %Y


class BaseBlock:
    """Base methods relied upon other, more complex ones down the line
    Docs: https://api.slack.com/reference/block-kit/composition-objects#text
    """
    AT_HERE = '<!here>'
    AT_CHANNEL = '<!channel>'

    @classmethod
    def length_assert(cls, item: Union[str, List], item_name: str, max_l: int):
        item_len = len(item)
        if item_len > max_l:
            raise StringExceededMaxLengthException(f'The item "{item_name}" exceeded the max length '
                                                   f'({max_l} v. {item_len}). ')

    @classmethod
    def perform_assertions(cls, assertions: Dict[str, Tuple[Union[str, List], int]]):
        for name, (obj, max_l) in assertions.items():
            if obj is None:
                continue
            cls.length_assert(obj, item_name=name, max_l=max_l)

    @classmethod
    def build_link(cls, url: str, text: str) -> str:
        """Generates a link into slack's expected format"""
        return f'<{url}|{text}>'

    @classmethod
    def localize_dates(cls, dt_obj: Union[date, datetime], format_type: DateFormatType) -> str:
        """Converts a date object into timestamp and places it in a text object that Slack knows how to parse
        to show localized dates/times for the end user
        References:
            https://api.slack.com/reference/surfaces/formatting#date-formatting
        """
        if isinstance(dt_obj, date):
            dt_obj = datetime.combine(dt_obj, time.min)
        return f'<!date^{int(round(dt_obj.timestamp()))}^{format_type.name}|{dt_obj.astimezone():%F %T %Z}>'

    @classmethod
    def _text(cls, text: str) -> str:
        cls.perform_assertions({
            'text': (text, 3000)
        })
        return text

    @classmethod
    def plaintext_section(cls, text: str, emoji: bool = True) -> PlainTextObjectType:
        """Generates a plaintext area in a block"""

        return {
            'type': 'plain_text',
            'text': cls._text(text=text),
            'emoji': emoji
        }

    @classmethod
    def markdown_section(cls, text: str, verbatim: bool = False) -> MarkdownTextObjectType:
        """Generates the generic text area in a block. NB! 'emoji' key is always False for these.
        Args:
            text: the text to input
            verbatim: when False, URLs will be auto-converted into links, conversation names will be linkified
                and certain mentions will be automatically parsed.
        """
        return {
            'type': 'mrkdwn',
            'text': cls._text(text=text),
            'emoji': False,
            'verbatim': verbatim
        }


    # TODO: Refactor below
    # @classmethod
    # def build_accessory_section(cls, accessory_type: str, action_id: str = None, placeholder_txt: str = None,
    #                             url: str = None, text: str = None, image_url: str = None, alt_text: str = None,
    #                             value: str = None, options_list: ListOfNestedDicts = None) -> \
    #         Union[NestedDict, BaseDict]:
    #     """Makes an accessory section for a given element"""
    #     # Optional attributes that are added if their values aren't empty
    #     optionals = {
    #         'url': url,
    #         'action_id': action_id,
    #         'value': value,
    #         'placeholder': cls.plaintext_section(placeholder_txt) if placeholder_txt is not None else None,
    #         'text': cls.plaintext_section(text) if text is not None else None,
    #         'options': options_list,
    #         'image_url': image_url,
    #         'alt_text': alt_text,
    #     }
    #     accessory_dict = {
    #         'type': accessory_type
    #     }
    #     for k, v in optionals.items():
    #         if v is not None:
    #             accessory_dict[k] = v
    #
    #     return accessory_dict

