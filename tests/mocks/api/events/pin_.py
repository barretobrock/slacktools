from tests.mocks.api import (
    FAKEAUTHORBOT,
    FAKEAUTHORNAME,
    FAKEAUTHORUSER,
    FAKECHANNEL,
    FAKELINK,
    FAKEPINNER,
    FAKETEAM,
    ts,
)

PIN_ADDED_EVENT_USR_RESP = {
    # Normal event response from pin_added
    'type': 'pin_added',
    'user': FAKEPINNER,
    'channel_id': FAKECHANNEL,
    'item': {
        'created_by': FAKEPINNER,
        'message': {
            'user': FAKEAUTHORUSER,
            'username': FAKEAUTHORNAME,
            'type': 'message',
            'text': "Something...",
            'ts': f'{ts}',
            'team': FAKETEAM,
            'blocks': [],
            'pinned_to': [FAKECHANNEL],
            'permalink': FAKELINK
        }
    },
    'event_ts': f'{ts}'
}

PIN_ADDED_EVENT_BOT_RESP = {
    # Normal event response from pin_added, but message is from a bot
    'type': 'pin_added',
    'user': FAKEPINNER,
    'channel_id': FAKECHANNEL,
    'item': {
        'type': 'message',
        'created': int(ts),
        'created_by': FAKEPINNER,
        'channel': FAKECHANNEL,
        'message': {
            'bot_id': FAKEAUTHORBOT,
            'type': 'message',
            'text': "Something...",
            'user': FAKEAUTHORUSER,
            'ts': f'{ts}',
            'team': FAKETEAM,
            'bot_profile': {},
            'blocks': [],
            'pinned_to': [FAKECHANNEL],
            'permalink': FAKELINK
        }
    },
    'event_ts': f'{ts}'
}

PIN_EVENT_REMOVED_RESP = {
    'type': 'pin_removed',
    'user': FAKEPINNER,
    'channel_id': FAKECHANNEL,
    'item': {
        'type': 'message',
        'created': int(ts),
        'created_by': FAKEAUTHORUSER,
        'channel': FAKECHANNEL,
        'message': {
            'type': 'message',
            'text': 'Something...',
            'user': FAKEAUTHORUSER,
            'ts': f'{ts}',
            'team': FAKETEAM,
            'blocks': [],
            'permalink': FAKELINK
        }
    },
    'event_ts': f'{ts}'
}
