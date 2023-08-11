from typing import Dict

from tests.common import random_string


def build_mock_slash_resp(command: str = '/hello', text: str = '', channel_name: str = 'test',
                          uid: str = 'USLKJWEI21') -> Dict:
    return {
        'token': random_string(n_chars=24),
        'team_id': random_string(n_chars=10),
        'team_domain': 'thetestdomain',
        'channel_id': random_string(n_chars=9).upper(),
        'channel_name': channel_name,
        'user_id': uid,
        'user_name': 'test-user',
        'command': command,
        'text': text,
        'api_app_id': random_string(n_chars=8).upper(),
        'response_url': 'https://hooks.slack.com/commands/ALKDSJFE/239847938417/thisisatest',
        'trigger_id': 'f12348713.32498734.12o138473294729734979174984159'
    }
