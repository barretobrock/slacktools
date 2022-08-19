from datetime import datetime
from typing import Dict

from tests.common import random_string


def build_mock_message_event(text: str = 'this is a test', uid: str = 'USLKJWEI21', ts: str = None,
                             is_bot: bool = False, is_thread: bool = False, channel_type: str = 'channel') -> Dict:
    _ts = f'{datetime.now().timestamp()}' if ts is None else ts
    resp_dict = {
        'type': 'message',
        'text': text,
        'user': uid,
        'ts': _ts,
        'team': random_string(n_chars=10).upper(),
        'blocks': [],
        'channel': random_string(n_chars=12).upper(),
        'event_ts': _ts,
        'channel_type': channel_type
    }
    if is_bot:
        resp_dict['bot_id'] = f'B{uid[1:]}'
    if is_thread:
        resp_dict['thread_ts'] = _ts

    return resp_dict
