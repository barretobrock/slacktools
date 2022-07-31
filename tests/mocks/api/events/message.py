from tests.mocks.api import (
    FAKEUSER,
    FAKEBOT,
    FAKECHANNEL,
    FAKETEAM,
    ts
)

MESSAGE_EVENT_USR_RESP = {
    'type': 'message',
    'text': 'test',
    'user': FAKEUSER,
    'ts': f'{ts}',
    'team': FAKETEAM,
    'blocks': [],
    'channel': FAKECHANNEL,
    'event_ts': f'{ts}',
    'channel_type': 'channel'
}

MESSAGE_EVENT_BOT_RESP = {
    'bot_id': FAKEBOT,
    'type': 'message',
    'text': 'Something',
    'user': FAKEUSER,
    'ts': f'{ts}',
    'team': FAKETEAM,
    'bot_profile': {},
    'blocks': [],
    'channel': FAKECHANNEL,
    'event_ts': f'{ts}',
    'channel_type': 'channel'
}
