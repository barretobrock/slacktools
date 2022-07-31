from pathlib import Path
import unittest
from unittest.mock import MagicMock

from slacktools.tools import (
    SlackTools,
    build_commands,
)
from tests.common import (
    get_test_logger,
    make_patcher,
    random_string,
)


class TestBotObj:
    def __getattr__(self, item):
        return 'item'


class TestBuildCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def setUp(self) -> None:
        self.test_bot_obj = TestBotObj()
        self.cmds = self.load_cmds()

    def load_cmds(self):
        return build_commands(self.test_bot_obj, Path(__file__).parent.joinpath('mocks/mock_commands.yaml'), log=self._log)

    def test_build_command(self):
        """Tests build_command_output"""
        self.assertGreaterEqual(len(self.cmds), 1)


class TestSlackTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def setUp(self) -> None:
        self.mock_webclient = make_patcher(self, 'slacktools.slack_methods.WebClient')
        self.mock_session = make_patcher(self, 'slacktools.slack_methods.SlackSession')
        self.mock_cred_entry = MagicMock(name='bot_cred_entry')
        self.mock_cred_name = 'something'

        self.st = SlackTools(bot_cred_entry=self.mock_cred_entry, parent_log=self._log, use_session=False)

    def test_init(self):
        self.mock_webclient.assert_called()
        self.st.bot.auth_test.assert_called()
        self.mock_session.assert_not_called()
        # Test init when use_session is True, but no cookie, xoxc keys provided
        self.st = SlackTools(bot_cred_entry=self.mock_cred_entry, parent_log=self._log, use_session=True)
        self.mock_session.assert_not_called()

        # Test init when use_session is True, but cookie and xoxc keys provided
        self.mock_cred_entry.d_cookie = 'aoe'
        self.mock_cred_entry.xoxc_token = 'tasoid'
        self.st = SlackTools(bot_cred_entry=self.mock_cred_entry, parent_log=self._log, use_session=True)
        self.mock_session.assert_called()

    def test_refresh_xoxc_token(self):
        self.mock_session.refresh_xoxc_token_and_cookie.assert_not_called()

    def test_parse_tag_from_text(self):
        expect = 'THIS32KJ'
        raw_txt = f'<@{expect}>'
        self.assertEqual(expect, self.st.parse_tag_from_text(raw_txt.upper()))
        self.assertEqual(expect, self.st.parse_tag_from_text(raw_txt.lower()))

    def test_build_emoji_char_dict(self):
        resp = self.st._build_emoji_char_dict()
        self.assertIsInstance(resp, dict)
        self.assertGreater(len(resp), 26)

    def test_build_phrase(self):
        # First, confirm all characters have been converted into emojis
        resp = self.st.build_phrase('hello this is a test 23.!')
        self.assertNotIn(' ', resp)
        # No dollar sign mapping, so that should come through
        resp = self.st.build_phrase('hello$$')
        self.assertIn('$', resp)

    def test_search_message_by_date(self):
        mock_resp = MagicMock(name='SlackResponse')
        v = {'ok': True}
        mock_resp.get.side_effect = v.get
        mock_resp.data = {}
        self.st.user.search_messages.return_value = mock_resp

        resp = self.st.search_messages_by_date(channel=random_string(20))
        self.st.user.search_messages.assert_called()
        self.assertIsNone(resp)


if __name__ == '__main__':
    unittest.main()
