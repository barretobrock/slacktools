import time
from datetime import (
    datetime,
    timedelta
)
import requests
from io import BytesIO
from asyncio import Future
from types import SimpleNamespace
from typing import (
    Union,
    List,
    Optional,
    Tuple,
    Dict
)
from loguru import logger
from slack import WebClient
from slack.web.slack_response import SlackResponse
from slack.errors import SlackApiError
from slacktools.slack_session import SlackSession


class SlackMethods:

    def __init__(self, bot_cred_entry: SimpleNamespace, parent_log: logger, use_session: bool = False):

        self.log = parent_log
        # Get team name
        self.team = bot_cred_entry.team
        # Grab tokens
        self.xoxp_token = bot_cred_entry.xoxp_token
        self.xoxb_token = bot_cred_entry.xoxb_token
        self.log.debug('Spinning up user and bot methods...')
        self.user = WebClient(self.xoxp_token)
        self.bot = WebClient(self.xoxb_token)
        self.log.debug('Retrieving bot id with an authentication test...')
        auth_test = self.bot.auth_test()
        self.bot_id = auth_test['bot_id']
        self.user_id = auth_test['user_id']

        self.session = self.d_cookie = self.xoxc_token = None
        if use_session:
            self.log.debug('Param `use_session` set to True - establishing session object.')
            if all([x in bot_cred_entry.__dict__.keys() for x in ['d_cookie', 'xoxc_token']]):
                self.d_cookie = bot_cred_entry.d_cookie
                self.xoxc_token = bot_cred_entry.xoxc_token
                self.session = SlackSession(self.team, d_cookie=self.d_cookie, xoxc_token=self.xoxc_token,
                                            parent_log=self.log)
            else:
                self.log.warning('Session was prevented from instantiating - either d_cookie or xoxc_token '
                                 'attributes weren\'t found in the cred entry.')

    @staticmethod
    def _check_for_exception(response: Union[Future, SlackResponse]):
        """Checks API response for exception info.
        If error, will return error message and any additional info
        """
        if response is None:
            raise ValueError('Response object was of NoneType.')
        else:
            if not response['ok']:
                # Error occurred
                err_msg = response['error']
                if err_msg == 'missing_scope':
                    err_msg += '\nneeded: {needed}\n'.format(**response.data)
                raise Exception(err_msg)

    @staticmethod
    def clean_user_info(user_dict: dict) -> dict:
        """Takes in a user dict of the user's info and flattens it,
        returning a flat dictionary of only the useful data"""
        return {
            'id': user_dict['id'],
            'name': user_dict['name'],
            'real_name': user_dict['real_name'],
            'is_bot': user_dict['is_bot'],
            'title': user_dict['profile']['title'],
            'display_name': user_dict['profile']['display_name'],
            'status_emoji': user_dict['profile']['status_emoji'],
            'status_text': user_dict['profile']['status_text'],
            'avi_hash': user_dict['profile']['avatar_hash'],
            'avi': user_dict['profile']['image_512'],
            'avi32': user_dict['profile']['image_32'],
        }

    def get_channel_members(self, channel: str, humans_only: bool = False) -> List[dict]:
        """Collect members of a particular channel
        Args:
            channel: str, the channel to examine
            humans_only: bool, if True, will only return non-bots in the channel
        """
        self.log.debug(f'Getting channel members for channel {channel}.')
        resp = self.bot.conversations_members(channel=channel)

        # Check response for exception
        self._check_for_exception(resp)
        user_ids = resp['members']
        users = []
        for user in self.get_users_info(user_ids):
            users.append(self.clean_user_info(user))

        return [user for user in users if not user['is_bot']] if humans_only else users

    def get_users_info(self, user_list: List[str], throw_exception: bool = True) -> List[dict]:
        """Collects info from a list of user ids"""
        self.log.debug('Collecting users\' info.')
        user_info = []
        for user in user_list:
            respdata = self.get_user_info(user_id=user, throw_exception=throw_exception)
            if 'user' in respdata.keys():
                user_info.append(respdata['user'])
        return user_info

    def get_user_info(self, user_id: str, throw_exception: bool = False) -> Dict:
        """Gets individual user info"""
        resp = None
        respdata = None
        try:
            resp = self.bot.users_info(user=user_id)
            respdata = resp.data
        except SlackApiError:
            if throw_exception:
                self._check_for_exception(resp)
            if resp['error'] == 'user_not_found':
                # Unsuccessful at finding user. Add in a placeholder.
                self.log.debug(f'User not found: {user_id}.')
                respdata = {
                    'user': {
                        'id': user_id,
                        'real_name': 'Unknown User',
                        'name': 'unknown_user',
                        'display_name': 'unknown_user',
                    }
                }
        return respdata

    def open_dialog(self, dialog: Dict, trigger_id: str, **kwargs):
        """Open a dialog with a user by passing in a trigger id received from another interaction"""
        resp = self.bot.dialog_open(dialog=dialog, trigger_id=trigger_id, **kwargs)
        # Check response for exception
        self._check_for_exception(resp)

    def update_home_tab(self, user_id: str, blocks: List[Dict]):
        """Updates the app's home tab with info"""
        self.bot.views_publish(user_id=user_id, view={
            'type': 'home',
            'blocks': blocks
        })

    def private_channel_message(self, user_id: str, channel: str, message: str, ret_ts: bool = False,
                                **kwargs) -> Optional[str]:
        """Send a message to a user on the channel"""
        self.log.debug(f'Sending private channel message: {channel} to {user_id}.')
        resp = self.bot.chat_postEphemeral(channel=channel, user=user_id, text=message, **kwargs)
        # Check response for exception
        self._check_for_exception(resp)
        if ret_ts:
            # Return the timestamp from the message
            return resp['message_ts']

    def private_message(self, user_id: str, message: str, ret_ts: bool = False,
                        **kwargs) -> Optional[Tuple[str, str]]:
        """Send private message to user"""
        self.log.debug(f'Sending private message to {user_id}.')
        # Grab the DM "channel" associated with the user
        resp = self.bot.conversations_open(users=user_id)
        dm_chan = resp['channel']['id']
        # Check response for exception
        self._check_for_exception(resp)
        # DM the user
        ts = self.send_message(channel=dm_chan, message=message, ret_ts=ret_ts, **kwargs)
        if ret_ts:
            # Return the timestamp from the message
            return dm_chan, ts

    def send_message(self, channel: str, message: str, ret_ts: bool = False, ret_all: bool = False,
                     **kwargs) -> Optional[Union[str, SlackResponse]]:
        """Sends a message to the specific channel"""
        self.log.debug(f'Sending channel message in {channel}.')
        resp = self.bot.chat_postMessage(channel=channel, text=message, **kwargs)
        self._check_for_exception(resp)
        if ret_ts:
            # Return the timestamp from the message
            return resp['ts']
        if ret_all:
            return resp

    def update_message(self, channel: str, ts: str, message: str = None, blocks: List[dict] = None):
        """Updates a message"""
        self.log.debug(f'Updating message in {channel}.')
        resp = self.bot.chat_update(channel=channel, ts=ts, text=message, blocks=blocks)
        self._check_for_exception(resp)

    def delete_message(self, message_dict: dict = None, channel: str = None, ts: str = None):
        """Deletes a given message
        NOTE: Since messages are deleted by channel id and timestamp, it's recommended to
            use search_messages_by_date() to determine the messages to delete
        """
        self.log.debug(f'Attempting to delete message in {channel}.')
        if message_dict is None and any([x is None for x in [channel, ts]]):
            raise ValueError('Either message_dict should have a value or provide a channel id and timestamp.')
        if message_dict is not None:
            resp = self.user.chat_delete(channel=message_dict['channel']['id'], ts=message_dict['ts'])
        else:
            resp = self.user.chat_delete(channel=channel, ts=ts)
        self._check_for_exception(resp)

    def get_channel_history(self, channel: str, limit: int = 1000) -> List[dict]:
        """Collect channel history"""
        self.log.debug(f'Getting channel history for channel {channel}.')
        resp = self.bot.conversations_history(channel=channel, limit=limit)
        self._check_for_exception(resp)
        return resp['messages']

    def create_channel(self, channel_name: str, is_private: bool = False):
        """Creates a public/private channel"""
        self.log.debug(f'Creating channel {channel_name} as a {"private" if is_private else "public"} channel')

    def invite_to_channel(self, channel: str, user_list: List[str]):
        """Invites a list of users to a given channel"""
        self.log.debug(f'Inviting users: {user_list} to channel {channel}')
        resp = self.bot.channels_invite(channel=channel, user=','.join(user_list))
        self._check_for_exception(resp)

    def search_messages_by_date(self, channel: str = None, from_uid: str = None, after_date: datetime = None,
                                after_ts: datetime = None, on_date: datetime = None, during_m: datetime = None,
                                has_emoji: str = None, has_pin: bool = None,
                                max_results: int = 100) -> Optional[List[dict]]:
        """Search for messages in a channel after a certain date

        Args:
            channel: str, the channel (e.g., "#channel")
            from_uid: str, the user id to filter on (no '<@' prefix)
            after_date: datetime, the (inclusive) date after which to examine.
                    cannot be used with other date filters
            after_ts: datetime, after querying, will further filter messages based on specific timestamp here
            on_date: datetime, the date to filter on. cannot be used with other date filters
            during_m: datetime, the most month period to filter on.
            has_emoji: str, filters on messages containing a certain emoji (':this-with-colon:')
            has_pin: bool, filters on whether the message is pinned
            max_results: int, the maximum number of results per page to return

        Returns: list of dict, channels matching the query

        Notes: more on search modifiers here: https://slack.com/help/articles/202528808-Search-in-Slack
        """
        self.log.debug('Beginning query build for message search.')
        slack_date_fmt = '%m-%d-%Y'  # Slack has a specific format to adhere to when in the US lol
        # Begin building queries
        query = ''
        if channel is not None:
            query += f'in:{channel}'
        if from_uid is not None:
            query += f' from:<@{from_uid}>'

        if after_date is not None:
            # Made this inclusive to avoid excluding the entire date
            query += f' after:{(after_date - timedelta(days=1)).strftime(slack_date_fmt)}'
        elif on_date is not None:
            query += f' on:{on_date.strftime(slack_date_fmt)}'
        elif during_m is not None:
            query += f' during:{during_m.strftime("%B").lower()}'
        if has_emoji is not None:
            query += f' has:{has_emoji}'
        if has_pin is not None:
            if has_pin:
                query += ' has:pin'

        self.log.debug(f'Sending query: {query}.')
        resp = None
        for attempt in range(3):
            resp = self.user.search_messages(
                query=query,
                count=max_results
            )
            try:
                self._check_for_exception(resp)
                break
            except Exception as e:
                print('Call failed. Error: {}'.format(e))
                time.sleep(2)

        if resp is None:
            return None

        if 'messages' in resp.data.keys():
            msgs = resp['messages']['matches']
            if after_ts is not None:
                filtered_msgs = [x for x in msgs if float(x['ts']) >= after_ts.timestamp()]
                return filtered_msgs
            return msgs

        return None

    def upload_file(self, channel: str, filepath: str, filename: str, is_url: bool = False, txt: str = ''):
        """Uploads the selected file to the given channel"""
        self.log.debug(f'Attempting to upload file to {channel}.')
        if is_url:
            file = requests.get(filepath)
            fbytes = BytesIO(file.content)
        else:
            fbytes = open(filepath, 'rb')

        resp = self.bot.files_upload(
            file=fbytes,
            channels=channel,
            filename=filename,
            initial_comment=txt
        )
        self._check_for_exception(resp)

    def get_emojis(self) -> Dict[str, str]:
        """Returns a dict of emojis for a given workspace"""
        resp = self.bot.emoji_list()
        self._check_for_exception(resp)
        return resp['emoji']

    def get_previous_msg_in_channel(self, channel: str, timestamp: str) -> Optional[Dict]:
        """Gets the previous message from the channel"""
        self.log.debug(f'Getting previous message in channel {channel}')
        resp = self.bot.conversations_history(
            channel=channel,
            latest=timestamp,
            limit=10)
        if not resp['ok']:
            return None
        if 'messages' in resp.data.keys():
            msgs = resp['messages']
            last_msg = msgs[0]
            return last_msg
        return None