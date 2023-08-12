import unittest

from slacktools.slack_session import SlackSession

from .common import make_patcher


class TestSlackSession(unittest.TestCase):

    def setUp(self) -> None:
        self.team_name = 'test_team'
        self.mock_cookie = 'coooooooooookie'
        self.mock_xoxc_token = 'xoxc-234239084-2349823749182374'
        self.mock_session = make_patcher(self, 'slacktools.slack_session.requests.session')
        self.slack_session = SlackSession(
            team=self.team_name,
            d_cookie=self.mock_cookie,
            xoxc_token=self.mock_xoxc_token
        )

    def test_init(self):
        expected_header = {'Cookie': self.mock_cookie}
        self.assertEqual(self.slack_session.team, self.team_name)
        self.assertEqual(self.slack_session.d_cookie, self.mock_cookie)
        self.assertEqual(self.slack_session.xoxc_token, self.mock_xoxc_token)
        self.assertEqual(self.slack_session.url_customize, f'https://{self.team_name}.slack.com/customize/emoji')
        self.assertDictEqual(self.slack_session.session.headers, expected_header)


if __name__ == '__main__':
    unittest.main()
