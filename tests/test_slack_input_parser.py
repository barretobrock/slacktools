import unittest

from slacktools.slack_input_parser import SlackInputParser


class TestSlackInputParser(unittest.TestCase):

    def test_parse_tag_from_text(self):
        tag = 'u2sl39847'
        no_tag = 'hello'
        with_tag = f'<@{tag}> a;sldfkjwo <WOW>'

        self.assertIsNone(SlackInputParser.parse_tag_from_text(no_tag))
        self.assertEqual(tag.upper(), SlackInputParser.parse_tag_from_text(with_tag))

    def test_parse_flags_from_command(self):
        cmd = 'this is my command'
        flag1_name = 'l'
        flag1_val = ''
        flag2_name = 'something'
        flag2_val = 'here are some words'

        msg = f'{cmd} -{flag1_name} {flag1_val} --{flag2_name} {flag2_val}'

        resp_dict = SlackInputParser.parse_flags_from_command(msg)
        self.assertEqual(cmd, resp_dict['cmd'])
        self.assertIn(flag1_name, resp_dict.keys())
        self.assertIn(flag2_name, resp_dict.keys())
        self.assertEqual(flag1_val, resp_dict[flag1_name])
        self.assertEqual(flag2_val, resp_dict[flag2_name])


if __name__ == '__main__':
    unittest.main()
