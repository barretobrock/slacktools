import unittest
from easylogger import Log
from slacktools.slacksession import SlackSession

team = ''
cookie = ''


class TestBlockKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls, bot='viktor') -> None:
        cls._log = Log('slacktools-test', log_level_str='DEBUG')
        cls.ss = SlackSession(team, cookie, cls._log)

    def setUp(self) -> None:
        pass

    def test_upload(self):
        self.ss.upload_emoji_from_url('')


if __name__ == '__main__':
    unittest.main()
