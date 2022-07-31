from tests.mocks.api import (
    FAKEAUTHORBOT,
    FAKEAUTHORUSER,
    FAKECHANNEL,
    FAKELINK,
    FAKEPINNER,
    FAKETEAM,
    ts,
)

PIN_API_USR_MSG_RESP = {
    # Normal API response item from pin.list
    'type': 'message',
    'created': int(ts),
    'created_by': FAKEPINNER,
    'channel': FAKECHANNEL,
    'message': {
        'type': 'message',
        'text': "something",
        'user': FAKEAUTHORUSER,
        'ts': f'{ts}',
        'team': FAKETEAM,
        'blocks': [],
        'pinned_to': [FAKECHANNEL],
        'permalink': FAKELINK
    }
}

PIN_API_BOT_MSG_RESP = {
    # Normal API response item from pin.list
    'type': 'message',
    'created': int(ts),
    'created_by': FAKEPINNER,
    'channel': FAKECHANNEL,
    'message': {
        'type': 'message',
        'text': "something",
        'bot_id': FAKEAUTHORBOT,
        'ts': f'{ts}',
        'team': FAKETEAM,
        'blocks': [],
        'pinned_to': [FAKECHANNEL],
        'permalink': FAKELINK
    }
}
