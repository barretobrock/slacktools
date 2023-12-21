import unittest

from slacktools.api.slash import SlashCommandEvent
from tests.common import get_test_logger
from tests.mocks.api.slash import build_mock_slash_resp


class TestSlash(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def test_slash(self):
        scenarios = {
            'oneword': {
                'raw': '/hello',
                'clean': 'hello'
            },
            'oneword with text': {
                'raw': '/hello',
                'clean': 'hello',
                'text': 'some command here idk\n a;lsdkrjeoir \\n a;dlkfjal;eeioaewur'
            },
            'dashed': {
                'raw': '/my-dashed-command',
                'clean': 'my dashed command'
            },
        }
        for scen, scen_dict in scenarios.items():
            self._log.debug(f'Working on scenario: {scen}')
            raw_cmd = scen_dict.get('raw')
            clean_cmd = scen_dict.get('clean')
            txt = scen_dict.get('text', '')
            full = f'{clean_cmd} {txt}' if txt != '' else clean_cmd
            slash = SlashCommandEvent(event_dict=build_mock_slash_resp(raw_cmd, txt))
            self.assertEqual(raw_cmd, slash.raw_command)
            self.assertEqual(clean_cmd, slash.cleaned_command)
            self.assertEqual(txt, slash.text)
            self.assertEqual(full, slash.cleaned_message)


if __name__ == '__main__':
    unittest.main()
