import unittest
from unittest.mock import MagicMock
from datetime import datetime
from slacktools.tools import SlackTools
from .common import (
    get_test_logger,
    make_patcher,
    random_string
)


class TestSlackTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def setUp(self) -> None:
        self.mock_gsr = make_patcher(self, 'slacktools.tools.GSheetReader')
        self.mock_webclient = make_patcher(self, 'slacktools.tools.WebClient')
        self.mock_session = make_patcher(self, 'slacktools.tools.SlackSession')
        self.mock_secret = MagicMock(name='SecretStore')
        self.mock_cred_name = 'something'

        self.st = SlackTools(credstore=self.mock_secret, slack_cred_name=self.mock_cred_name, parent_log=self._log,
                             use_session=False)

    def test_init(self):
        self.mock_webclient.assert_called()
        self.st.bot.auth_test.assert_called()
        self.mock_secret.get_key_and_make_ns.assert_called_with(self.mock_cred_name)
        self.mock_session.assert_not_called()
        # Test init when use_session is True
        self.st = SlackTools(credstore=self.mock_secret, slack_cred_name=self.mock_cred_name, parent_log=self._log,
                             use_session=True)
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
