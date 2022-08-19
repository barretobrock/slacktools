import unittest

from slacktools.api.events.pin_added_or_removed import (
    PinEvent,
    PinType,
)
from tests.common import get_test_logger
from tests.mocks.api.pin import build_mock_pin_event


class TestPinAddedOrRemoved(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def test_event_pin_author_user(self):
        uid = 'UAL::LKEO'
        pin_event = build_mock_pin_event(PinType.pin_added, uid=uid)
        pin_obj = PinEvent(event_dict=pin_event)
        self.assertEqual(uid, pin_obj.item.message.user)

    def test_event_pin_author_bot(self):
        """Tests when pin event triggered on bot's message"""
        uid = 'UAL::LKEO'
        bid = f'B{uid[1:]}'
        pin_event = build_mock_pin_event(PinType.pin_added, uid=uid, is_bot=True)
        pin_obj = PinEvent(event_dict=pin_event)
        self.assertEqual(bid, pin_obj.item.message.bot_id)
        self.assertIsNone(pin_obj.item.message.username)
