from datetime import (
    date,
    datetime,
    time,
)
import enum
from typing import (
    Dict,
    List,
    Tuple,
    Union,
)

from slacktools.block_kit.types import (
    MarkdownTextObjectType,
    PlainTextObjectType,
)


class StringExceededMaxLengthException(Exception):
    pass


class DateFormatType(enum.Enum):
    default = '{date_short_pretty} at {time_secs}'
    date_num = '{date_num}'                     # %Y-%m-%d
    date = '{date}'                             # %B %dth, %Y
    date_short = '{date_short}'                 # %b %d, %Y
    date_long = '{date_long}'                   # %A, %B %dth, %Y
    date_pretty = '{date_pretty}'               # yesterday, today => date
    date_short_pretty = '{date_short_pretty}'   # yesterday, today => date_short
    date_long_pretty = '{date_long_pretty}'     # yesterday, today => date_long
    time = '{time}'                             # %H:%M
    time_secs = '{time_secs}'                   # %H:%M:%S


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
    def _build_date_command(cls, timestamp: int, date_format_type: DateFormatType, fallback: datetime,
                            fallback_format: str = '%F %T %Z') -> str:
        return f'<!date^{timestamp}^{date_format_type.value}|{fallback.astimezone():{fallback_format}}>'

    @classmethod
    def localize_dates(cls, dt_obj: Union[date, datetime], format_type: DateFormatType,
                       fallback_format: str = '%F %T %Z') -> str:
        """Converts a date object into timestamp and places it in a text object that Slack knows how to parse
        to show localized dates/times for the end user
        References:
            https://api.slack.com/reference/surfaces/formatting#date-formatting
        """
        if isinstance(dt_obj, date):
            dt_obj = datetime.combine(dt_obj, time.min)
        return cls._build_date_command(timestamp=int(round(dt_obj.timestamp())), date_format_type=format_type,
                                       fallback=dt_obj, fallback_format=fallback_format)

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
            'verbatim': verbatim
        }
