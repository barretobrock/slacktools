import unittest
from unittest.mock import MagicMock, call

from slacktools.slack_methods import SlackMethods

from .common import make_patcher


class TestSlackMethods(unittest.TestCase):

    def setUp(self) -> None:
        # Set Variables
        # -------------------------------------------------------------------------------------------------------------
        self.team_name = 'test_team'
        self.mock_cookie = 'coooooooooookie'
        self.mock_xoxp_token = 'xoxp-2p34239084-2349823749182374ppp'
        self.mock_xoxb_token = 'xoxb-23b4239084-2349823749182374bbbb'
        self.mock_bot_id = 'AYYYY69'
        self.mock_user_id = 'LMAO420'

        # Build / populate mocks
        # -------------------------------------------------------------------------------------------------------------
        self.mock_webclient = make_patcher(self, 'slacktools.slack_methods.WebClient')
        self.mock_user_webclient = MagicMock(name='user')
        self.mock_bot_webclient = MagicMock(name='bot')
        self.mock_bot_webclient.auth_test.return_value = {
            'bot_id': self.mock_bot_id,
            'user_id': self.mock_user_id
        }

        self.mock_botcreds = MagicMock()
        self.mock_botcreds.team = self.team_name
        self.mock_botcreds.xoxp_token = self.mock_xoxp_token
        self.mock_botcreds.xoxb_token = self.mock_xoxb_token

        self.mock_webclient.side_effect = [
            self.mock_user_webclient,
            self.mock_bot_webclient
        ]
        # Call
        # -------------------------------------------------------------------------------------------------------------
        self.smethod = SlackMethods(
            bot_cred_entry=self.mock_botcreds,
            use_session=False
        )

    def test_init(self):
        # Set Variables
        # -------------------------------------------------------------------------------------------------------------

        # Build / populate mocks
        # -------------------------------------------------------------------------------------------------------------

        # Call
        # -------------------------------------------------------------------------------------------------------------

        # Assert
        # -------------------------------------------------------------------------------------------------------------
        self.assertEqual(self.smethod.team, self.team_name)
        self.assertEqual(self.smethod.xoxb_token, self.mock_xoxb_token)
        self.assertEqual(self.smethod.xoxp_token, self.mock_xoxp_token)
        self.mock_webclient.assert_has_calls([
            call(self.mock_xoxp_token),
            call(self.mock_xoxb_token)
        ])
        self.mock_bot_webclient.auth_test.assert_called_once()


if __name__ == '__main__':
    unittest.main()
