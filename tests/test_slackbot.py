from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from slacktools.slackbot import SlackBotBase
from slacktools.tools import (
    ProcessedCommandItemType,
    build_commands,
)

from .common import (
    get_test_logger,
    make_patcher,
)


class TestSlackBotBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def setUp(self) -> None:
        self.mock_webclient = make_patcher(self, 'slacktools.slack_methods.WebClient')
        self.mock_cred = MagicMock(spec=SimpleNamespace, team='theteam', xoxp_token='xoxp...',
                                   xoxb_token='xoxb...')

        self.sbb = SlackBotBase(bot_cred_entry=self.mock_cred, triggers=['hello'], main_channel='main')
        self.mock_webclient.assert_called()

    def test_build_command_output(self):
        """Tests build_command_output"""
        cmd_dict = ProcessedCommandItemType(
            pattern='^(ag|acro[-]?guess)',
            tags=['random', 'tow'],
            group='random',
            desc='Guess an acronym',
            examples=['ag CCC'],
            flags=['-(g|group) <group_name>'],
            response=['ok!']
        )
        resp = self.sbb.build_command_output(cmd_dict)
        self.assertIsInstance(resp, str)
        self.assertIn('Optional Flags:', resp)

    def test_build_help_block(self):
        resp = self.sbb.build_help_block(intro='test', avi_url='url', avi_alt='this is an alt description')
        self.assertIsInstance(resp, list)
        self.assertGreaterEqual(5, len(resp))

    def test_search_help_block(self):
        self.sbb.update_commands(
            build_commands(self.sbb, Path(__file__).parent.joinpath('mocks/mock_commands.yaml'), log=self._log)
        )
        resp = self.sbb.search_help_block('shelp -g linguistics')
        self.assertIsInstance(resp, list)
        self.assertEqual(2, len(resp))


if __name__ == '__main__':
    unittest.main()
