import unittest
from easylogger import Log
from slacktools.tools import SlackTools, BlockKitBuilder, SecretStore
from .mocks.slack_settings import settings


class TestSlackTools(unittest.TestCase):
    def setUp(self, bot='viktor') -> None:
        # Read in the kdbx of secrets
        credstore = SecretStore('secretprops-bobdev.kdbx')
        _log = Log('slacktools-test', log_level_str='DEBUG')
        self.st = SlackTools(credstore=credstore, slack_cred_name=bot, parent_log=_log)
        bot_dict = settings [bot]
        self.test_channel = bot_dict['test_channel']
        self.test_user = bot_dict['test_user']
        self.bkb = BlockKitBuilder()

    def test_get_channel_members(self):
        self.st.get_channel_members(self.test_channel)

    def test_private_channel_message(self):
        self.st.private_channel_message(self.test_user, self.test_channel, 'Did ya get that thing I sent ya?')

    def test_send_message(self):
        self.st.send_message(self.test_channel, 'Testerino')

    def test_send_message_and_update(self):
        ts = self.st.send_message(self.test_channel, 'Testerino', ret_ts=True)
        self.st.update_message(self.test_channel, ts, 'Hello, this is updated')

    def test_send_message_and_update2(self):
        ts = self.st.send_message(self.test_channel, 'Testerino', ret_ts=True)
        block = [
            self.bkb.make_context_section([self.bkb.markdown_section('lol what context')]),
            self.bkb.make_block_divider(),
            self.bkb.make_block_section('testy test - best test has a zest of the west')
        ]
        self.st.update_message(self.test_channel, ts, blocks=block)

    def test_dm_and_update(self):
        dm_chan, ts = self.st.private_message(self.test_user, 'Testerino', ret_ts=True)
        self.st.update_message(dm_chan, ts, 'Hello, this is updated')

    def test_private_message(self):
        self.st.private_message(self.test_user, 'Testerino')

    def test_get_channel_history(self):
        self.st.get_channel_history(self.test_channel)

    def test_get_emojis(self):
        self.st.get_emojis()


if __name__ == '__main__':
    unittest.main()
