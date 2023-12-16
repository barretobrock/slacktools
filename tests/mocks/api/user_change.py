from datetime import datetime
from typing import Dict

from tests.common import random_string


def build_mock_user_change_resp(real_name: str, display_name: str, uid: str = 'USLKJWEI21',
                                status_text: str = '', status_emoji: str = '', ts: str = None,
                                is_admin: bool = False, is_bot: bool = False) -> Dict:
    _ts = f'{datetime.now().timestamp()}' if ts is None else ts
    team_id = random_string(n_chars=10).upper()

    resp_dict = dict(
        id=uid,
        team_id=team_id,
        name='email.name',
        deleted=False,
        color='acacac',
        real_name=real_name,
        tz='America/Chicago',
        tz_label='Central Daylight Time',
        tz_offset=-18000,
        profile=dict(
            title='',
            phone='5555555555',
            skype='',
            real_name=real_name,
            real_name_normalized=real_name,
            display_name=display_name,
            display_name_normalized=display_name,
            fields={
                'Xf01FAKECUSTOMFIELD1': {
                    'value': 'Something',
                    'alt': ''
                },
            },
            status_text=status_text,
            status_emoji=status_emoji,  # ":hello:"
            status_emoji_display_info=[],
            status_expiration=0,
            avatar_hash=random_string(14),
            pronouns='',
            first_name=real_name,
            last_name='',
            image_24='fakelink',
            image_32='fakelink',
            image_48='fakelink',
            image_72='fakelink',
            image_192='fakelink',
            image_512='fakelink',
            status_text_canonical='',
            team=team_id
        ),
        is_admin=is_admin,
        is_owner=False,
        is_primary_owner=False,
        is_restricted=False,
        is_ultra_restricted=False,
        is_bot=is_bot,
        is_app_user=False,
        updated=int(float(_ts)),
        is_email_confirmed=True,
        who_can_share_contact_card='EVERYONE',
        locale='en-US'
    )

    return {'user': resp_dict}
