import unittest
from kavalkilu import Keys
from slacktools.tools import SlackTools, BlockKitBuilder


keys = {
    'viktor': {
        'xoxp': 'kodubot-usertoken',
        'xoxb': 'kodubot-useraccess',
        'team': 'okr-name',
        'test_channel': 'CM376Q90F',
        'test_user': 'UM35HE6R5'
    },
    'cah': {
        'xoxp': 'wizzy-token',
        'xoxb': 'wizzy-bot-user-token',
        'team': 'okr-name',
        'test_channel': 'CM376Q90F',
        'test_user': 'UM35HE6R5'
    },
    'dnd': {
        'xoxp': 'dizzy-token',
        'xoxb': 'dizzy-bot-user-token',
        'team': 'dnd',
        'test_channel': 'CT48WCESG',
        'test_user': 'USS6FQ283'
    }
}


class TestSlackTools(unittest.TestCase):
    def setUp(self, bot='viktor') -> None:
        get_key = Keys().get_key
        bot_dict = keys[bot]
        self.st = SlackTools(team=get_key(bot_dict['team']),
                             xoxp_token=get_key(bot_dict['xoxp']), xoxb_token=get_key(bot_dict['xoxb']))
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
            self.bkb.make_context_section('lol what context'),
            self.bkb.make_block_divider(),
            self.bkb.make_block_section('testy test - best test is a zest of the west')
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
