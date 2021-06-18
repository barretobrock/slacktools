import unittest
from easylogger import Log
from slacktools.tools import SlackTools, BlockKitBuilder as bkb, SecretStore
from .mocks.slack_settings import settings


class TestBlockKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls, bot='viktor') -> None:
        # Read in the kdbx of secrets
        credstore = SecretStore('secretprops-bobdev.kdbx')
        cls._log = Log('slacktools-test', log_level_str='DEBUG')
        cls.st = SlackTools(credstore=credstore, slack_cred_name=bot, parent_log=cls._log)
        bot_dict = settings[bot]
        cls.test_channel = bot_dict['test_channel']
        cls.test_user = bot_dict['test_user']

    def setUp(self) -> None:
        options = ['you could go with this', 'or you could go with that', 'you could go with this',
                   'or you could go with          that']
        options_list = [{'txt': x, 'value': f'{i}'} for i, x in enumerate(options)]

        self.test_form = [
            bkb.make_header('This is a header'),
            bkb.make_block_divider(),
            bkb.make_static_select('Select a single value here', options_list),
            bkb.make_multi_user_select('Select multiple users')
        ]

    def test_build_form(self):
        self.st.send_message(self.test_channel, message='Test message', blocks=self.test_form)

    def test_open_dialog(self):
        dialog = {
            'callback_id': 'hello-1234',
            'title': 'Don\'t Get Testy With Me',
            'submit_label': 'Submit',
            'state': 'Hello',
            'elements': [self.test_form[2:]]
        }
        self.st.open_dialog(dialog, '13345224609.738474920.8088930838d88f008e0')

    def test_menu_in_message(self):
        """Tests generating a small menu within a message"""
        options = [
            bkb.make_menu_option('dickneck', 'Dickneck', 'dickneck'),
            bkb.make_menu_option('buttnutt', 'Buttnutt', 'buttnutt'),
            bkb.make_menu_option('milfred', 'Milfred', 'milfred', incl_confirm=True, confirm_title='U sure?',
                                 confirm_text='Hey are you ok bud?', ok_text='Ya', dismiss_text='Na')
        ]
        resp = self.st.send_message(self.test_channel, message='Sup dickneck',
                                    attachments=bkb.make_message_menu_attachment(
                                        title='How should I address you?', menu_options=options,
                                        fallback='idklol', callback_id='lol420'), ret_all=True)


if __name__ == '__main__':
    unittest.main()
