import datetime
import enum
from typing import Union


class TextFormatter:
    AT_CHANNEL = '<!channel>'
    AT_HERE = '<!here>'

    @classmethod
    def build_link(cls, url: str, link_name: str) -> str:
        return f'<{url}|{link_name}>'

    @classmethod
    def build_channel_mention(cls, channel_id: str) -> str:
        return f'<#{channel_id}>'

    @classmethod
    def build_user_mention(cls, user_id: str) -> str:
        return f'<@{user_id}>'


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


class DateFormatter:
    @classmethod
    def _build_date_command(cls, timestamp: int, format_text: str, fallback: datetime,
                            fallback_format: str = '%F %T %Z') -> str:
        return f'<!date^{timestamp}^{format_text}|{fallback.astimezone():{fallback_format}}>'

    @classmethod
    def localize_dates(cls, dt_obj: Union[datetime.date, datetime.datetime], format_text: str,
                       fallback_format: str = '%F %T %Z') -> str:
        f"""Converts a date object into timestamp and places it in a text object that Slack knows how to parse
        to show localized dates/times for the end user
        Example:
            my_str = "Hello, {DateFormatType.date_pretty.value} at {DateFormatType.time.value} we will have the thing"
            dt_obj = datetime.now()
            localize_dates(dt_obj, format_text=my_str)
        
        References:
            https://api.slack.com/reference/surfaces/formatting#date-formatting
        """
        # NB! checking instance between datetime and date yields True for both, thus we use the following
        if type(dt_obj) is datetime.date:
            dt_obj = datetime.datetime.combine(dt_obj, datetime.time.min)
        return cls._build_date_command(timestamp=int(round(dt_obj.timestamp())), format_text=format_text,
                                       fallback=dt_obj, fallback_format=fallback_format)
