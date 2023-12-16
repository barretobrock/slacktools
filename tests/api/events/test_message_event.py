import unittest

from slacktools.api.events.message import Message
from tests.common import get_test_logger
from tests.mocks.api.message import build_mock_message_event


class TestMessageEvent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def test_event(self):
        scenarios = {
            'oneword': {
                'raw': 'HELLO   ',
                'clean': 'hello'
            }
        }
        for scen, scen_dict in scenarios.items():
            self._log.debug(f'Working on scenario: {scen}')
            raw_cmd = scen_dict.get('raw')
            clean_cmd = scen_dict.get('clean')

            resp = Message(event_dict=build_mock_message_event(text=raw_cmd))
            resp.take_processed_message(clean_msg=clean_cmd, raw_message=raw_cmd)
            self.assertEqual(raw_cmd, resp.raw_message)
            self.assertEqual(clean_cmd, resp.cleaned_message)


if __name__ == '__main__':
    unittest.main()
