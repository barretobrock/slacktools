import unittest

from slacktools.api.events.user import UserProfileChanged
from tests.common import get_test_logger
from tests.mocks.api.user_change import build_mock_user_change_resp


class TestUserChangeEvent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def test_user_change(self):
        scenarios = {
            'new_status': {
                'new_status': 'test',
            },
        }
        for scen, scen_dict in scenarios.items():
            self._log.debug(f'Working on scenario: {scen}')
            new_status = scen_dict.get('new_status')
            resp = UserProfileChanged(event_dict=build_mock_user_change_resp(
                real_name='something',
                display_name='quicker',
                status_text=new_status
            ))
            self.assertEqual(new_status, resp.user.profile.status_text)


if __name__ == '__main__':
    unittest.main()
