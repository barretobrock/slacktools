import unittest

from slacktools.api.events.pin_added_or_removed import PinEvent
from tests.common import (
    get_test_logger,
)
from tests.mocks.api.events.pin_ import (
    FAKEAUTHORBOT,
    FAKEAUTHORUSER,
    PIN_EVENT_BOT_RESP,
    PIN_EVENT_USR_RESP
)


class TestPinAddedOrRemoved(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def test_event_pin_author_user(self):
        edict = PIN_EVENT_USR_RESP.copy()
        pin_obj = PinEvent(edict)
        self.assertEqual(FAKEAUTHORUSER, pin_obj.item.message.user)

    def test_event_pin_author_bot(self):
        """Tests when pin event triggered on bot's message"""
        edict = PIN_EVENT_BOT_RESP.copy()
        pin_obj = PinEvent(edict)
        self.assertEqual(FAKEAUTHORBOT, pin_obj.item.message.bot_id)
        self.assertIsNone(pin_obj.item.message.user)
