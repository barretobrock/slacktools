from tests.mocks.api import (
    FAKEAUTHORBOT,
    FAKEAUTHORUSER,
    FAKEPINNER,
    FAKECHANNEL,
    FAKELINK,
    FAKEAUTHORNAME,
    ts
)


PIN_EVENT_USR_RESP = {
    # Normal event response from pin_added
    'type': 'pin_added',
    'user': FAKEPINNER,
    'channel_id': FAKECHANNEL,
    'item': {
        'message': {
            'user': FAKEAUTHORUSER,
            'username': FAKEAUTHORNAME,
            'created_by': FAKEPINNER,
        }
    },
    'event_ts': f'{ts}'
}

PIN_EVENT_BOT_RESP = {
    # Normal event response from pin_added, but message is from a bot
    'type': 'pin_added',
    'user': FAKEPINNER,
    'channel_id': FAKECHANNEL,
    'item': {
        'message': {
            'bot_id': FAKEAUTHORBOT,
            'created_by': FAKEAUTHORBOT,
        }
    },
    'event_ts': f'{ts}'
}
