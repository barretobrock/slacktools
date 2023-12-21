from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from slacktools.api.events.message import Message
from slacktools.api.slash.slash import SlashCommandEvent
from slacktools.slackbot import SlackBotBase
from slacktools.tools import (
    ProcessedCommandItemType,
    build_commands,
)

from .common import (
    get_test_logger,
    make_patcher,
)
from .mocks.api.message import build_mock_message_event
from .mocks.api.slash import build_mock_slash_resp


class TestSlackBotBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()

    def setUp(self) -> None:
        self.mock_webclient_user = MagicMock(name='WebClient(User)')
        self.mock_webclient_bot = MagicMock(name='WebClient(Bot)')
        mock_webclient = make_patcher(self, 'slacktools.slack_methods.WebClient')
        mock_webclient.side_effect = [
            self.mock_webclient_user,
            self.mock_webclient_bot
        ]
        self.mock_props = {
            'team': 'test-team',
            'xoxp-token': 'xoxp...',
            'xoxb-token': 'xoxb...'
        }

        self.sbb = SlackBotBase(props=self.mock_props, triggers=['hello'], main_channel='main')
        self.mock_webclient_bot.auth_test.assert_called()

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

    def _build_mock_commands(self):
        self.sbb.update_commands(
            build_commands(self.sbb, Path(__file__).parent.joinpath('mocks/mock_commands.yaml'), log=self._log)
        )

    def test_search_help_block(self):
        self._build_mock_commands()
        resp = self.sbb.search_help_block('shelp -g linguistics')
        self.assertIsInstance(resp, list)
        self.assertEqual(2, len(resp))

    def test_handle_message(self):
        self._build_mock_commands()

        scenarios = {
            'text-only': {
                'message': 'good bot',
                'is_called': [self.mock_webclient_bot.chat_postMessage]
            },
            'shelp': {
                'message': 'shelp -t debug',
                'is_called': [self.mock_webclient_bot.chat_postMessage]
            }
        }

        for name, scen_dict in scenarios.items():
            self._log.debug(f'Running scenario: {name}')
            test_message_event = build_mock_message_event(scen_dict['message'])
            test_message_obj = Message(test_message_event)
            self.sbb.handle_command(test_message_obj)
            for item in scen_dict.get('is_called', []):
                item.assert_called()

    def test_handle_slash_command(self):
        self._build_mock_commands()

        scenarios = {
            'help': {
                'command': 'shelp -g ui',
                'is_called': [self.mock_webclient_bot.chat_postEphemeral]
            }
        }

        for name, scen_dict in scenarios.items():
            self._log.debug(f'Running scenario: {name}')
            test_slash_event = build_mock_slash_resp(scen_dict['command'])
            test_slash_obj = SlashCommandEvent(test_slash_event)
            self.sbb.handle_command(test_slash_obj)
            for item in scen_dict.get('is_called', []):
                item.assert_called()


if __name__ == '__main__':
    unittest.main()
