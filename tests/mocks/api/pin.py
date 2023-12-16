from datetime import datetime
from typing import Dict

from tests.common import random_string


def build_mock_pin_event(pin_type: str, text: str = 'this is a test', uid: str = 'USLKJWEI21', ts: str = None,
                         is_bot: bool = False) -> Dict:
    _ts = f'{datetime.now().timestamp()}' if ts is None else ts
    channel_id = random_string(12).upper()

    msg_item = dict(
        type='message',
        user=uid,
        username='some_user23',
        text=text,
        ts=_ts,
        team=random_string(8).upper(),
        blocks=[],
        pinned_to=[channel_id],
        permalink='fakelink'
    )
    if is_bot:
        msg_item.update({
            'bot_id': f'B{uid[1:]}',
            'bot_profile': {},
            'username': None
        })

    resp_dict = dict(
        type=pin_type,
        user=uid,
        channel_id=channel_id,
        item=dict(
            type='message',
            created=int(float(_ts)),
            created_by=uid,
            channel=channel_id,
            message=msg_item
        ),
        has_pins=True,
        event_ts=_ts
    )

    return resp_dict


def build_mock_pin_api_resp(text: str = 'this is a test', uid: str = 'USLKJWEI21', ts: str = None,
                            is_bot: bool = False) -> Dict:
    _ts = f'{datetime.now().timestamp()}' if ts is None else ts
    channel_id = random_string(12).upper()
    msg_item = dict(
        type='message',
        text=text,
        ts=_ts,
        team=random_string(8).upper(),
        blocks=[{}],
        pinned_to=[channel_id],
        permalink='fakelink'
    )
    if is_bot:
        msg_item['bot_id'] = f'B{uid[1:]}'
    else:
        msg_item['user'] = uid
    resp_dict = dict(
        type='message',
        created=int(float(_ts)),
        created_by=uid,
        channel=channel_id,
        message=msg_item
    )
    return resp_dict
