from asyncio import Future
from datetime import (
    datetime,
    timedelta,
)
from io import BytesIO
import time
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from loguru import logger
import requests
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient
from slack_sdk.web.slack_response import SlackResponse

from slacktools.api.web.conversations import (
    ConversationHistory,
    ConversationMembers,
    ConversationReply,
    Message,
    ThreadMessage,
)
from slacktools.api.web.users import UserInfo
from slacktools.block_kit.base import (
    BaseElement,
    BlocksType,
)
from slacktools.slack_session import SlackSession


class SlackMethods:

    def __init__(self, props: Dict, main_channel: str, use_session: bool = False):
        # Get team name
        self.team = props['team']
        self.main_channel = main_channel
        # Grab tokens
        self.xoxp_token = props['xoxp-token']
        self.xoxb_token = props['xoxb-token']
        logger.debug('Spinning up user and bot methods...')
        self.user = WebClient(self.xoxp_token)
        self.bot = WebClient(self.xoxb_token)
        logger.debug('Retrieving bot id with an authentication test...')
        auth_test = self.bot.auth_test()
        self.bot_id = auth_test['bot_id']
        self.user_id = auth_test['user_id']

        self.session = self.d_cookie = self.xoxc_token = None
        if use_session:
            logger.debug('Param `use_session` set to True - establishing session object.')
            if all([x in props.keys() for x in ['d-cookie', 'xoxc-token']]):
                self.d_cookie = props['d-cookie']
                self.xoxc_token = props['xoxc-token']
                self.session = SlackSession(self.team, d_cookie=self.d_cookie, xoxc_token=self.xoxc_token)
            else:
                logger.warning('Session was prevented from instantiating - either d_cookie or xoxc_token '
                               'attributes weren\'t found in the cred entry.')

    @staticmethod
    def _check_for_exception(response: Union[Future, SlackResponse], is_raise: bool = False):
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
                if is_raise:
                    raise Exception(err_msg)
                else:
                    logger.error(err_msg)

    def get_channel_members(self, channel: str, humans_only: bool = False) -> List[UserInfo]:
        """Collect members of a particular channel
        Args:
            channel: str, the channel to examine
            humans_only: bool, if True, will only return non-bots in the channel
        """
        logger.debug(f'Getting channel members for channel {channel}.')
        resp = self.bot.conversations_members(channel=channel)
        channel_members = ConversationMembers(resp.data)

        user_ids = channel_members.members
        users = []
        for user in self.get_users_info(user_ids):
            users.append(user)

        return [user for user in users if not user.is_bot] if humans_only else users

    def get_users_info(self, user_id_list: List[str], throw_exception: bool = True) -> List[UserInfo]:
        """Collects info from a list of user ids"""
        logger.debug('Collecting users\' info.')
        user_info_list = []
        for user in user_id_list:
            user_info_list.append(self.get_user_info(user_id=user, throw_exception=throw_exception))
        return user_info_list

    def get_user_info(self, user_id: str, throw_exception: bool = False) -> Optional[UserInfo]:
        """Gets individual user info"""
        user = resp = None
        try:
            resp = self.bot.users_info(user=user_id)
            user = UserInfo(resp['user'])
        except SlackApiError:
            self._check_for_exception(resp, is_raise=throw_exception)
            if resp['error'] == 'user_not_found':
                # Unsuccessful at finding user. Add in a placeholder.
                logger.error(f'User not found: {user_id}.')
                user = UserInfo(id=user_id, real_name='Unknown User', name='unknown_user', display_name='unknown_user')

        return user

    def open_dialog(self, dialog: Dict, trigger_id: str, **kwargs):
        """Open a dialog with a user by passing in a trigger id received from another interaction"""
        resp = self.bot.dialog_open(dialog=dialog, trigger_id=trigger_id, **kwargs)
        # Check response for exception
        self._check_for_exception(resp, is_raise=True)

    def update_home_tab(self, user_id: str, blocks: List[Dict]):
        """Updates the app's home tab with info"""
        self.bot.views_publish(user_id=user_id, view={
            'type': 'home',
            'blocks': blocks
        })

    def private_channel_message(self, user_id: str, channel: str, message: str, ret_ts: bool = False,
                                blocks: BlocksType = None, **kwargs) -> Optional[str]:
        """Send a message to a user on the channel"""
        logger.debug(f'Sending private channel message: {channel} to {user_id}.')

        if blocks is not None:
            blocks = self._dictify_blocks(blocks)

        resp = self.bot.chat_postEphemeral(channel=channel, user=user_id, text=message, blocks=blocks, **kwargs)
        # Check response for exception
        self._check_for_exception(resp, is_raise=True)
        if ret_ts:
            # Return the timestamp from the message
            return resp['message_ts']

    def private_message(self, user_id: str, message: str, ret_ts: bool = False, blocks: BlocksType = None,
                        **kwargs) -> Optional[Tuple[str, str]]:
        """Send private message to user"""
        logger.debug(f'Sending private message to {user_id}.')
        # Grab the DM "channel" associated with the user
        resp = self.bot.conversations_open(users=user_id)
        dm_chan = resp['channel']['id']
        # Check response for exception
        self._check_for_exception(resp, is_raise=True)

        if blocks is not None:
            blocks = self._dictify_blocks(blocks)

        # DM the user
        ts = self.send_message(channel=dm_chan, message=message, ret_ts=ret_ts, blocks=blocks, **kwargs)
        if ret_ts:
            # Return the timestamp from the message
            return dm_chan, ts

    @staticmethod
    def _dictify_blocks(blocks_list: BlocksType) -> List[Dict]:
        new_blocks = []
        for block in blocks_list:
            if isinstance(block, BaseElement):
                new_blocks.append(block.asdict())
            else:
                new_blocks.append(block)
        return new_blocks

    def send_message(self, channel: str, message: str = None, ret_ts: bool = False, ret_all: bool = False,
                     blocks: BlocksType = None, **kwargs) -> Optional[Union[str, SlackResponse]]:
        """Sends a message to the specific channel"""
        logger.debug(f'Sending channel message in {channel}.')
        if blocks is not None:
            blocks = self._dictify_blocks(blocks)

        resp = self.bot.chat_postMessage(channel=channel, text=message, blocks=blocks, **kwargs)
        self._check_for_exception(resp, is_raise=True)
        if ret_ts:
            # Return the timestamp from the message
            return resp['ts']
        if ret_all:
            return resp

    def update_message(self, channel: str, ts: str, message: str = None, blocks: BlocksType = None):
        """Updates a message"""
        logger.debug(f'Updating message in {channel}.')
        if blocks is not None:
            blocks = self._dictify_blocks(blocks)
        resp = self.bot.chat_update(channel=channel, ts=ts, text=message, blocks=blocks)
        self._check_for_exception(resp, is_raise=True)

    def delete_message(self, message_dict: dict = None, channel: str = None, ts: str = None):
        """Deletes a given message
        NOTE: Since messages are deleted by channel id and timestamp, it's recommended to
            use search_messages_by_date() to determine the messages to delete
        """
        logger.debug(f'Attempting to delete message in {channel}.')
        if message_dict is None and any([x is None for x in [channel, ts]]):
            raise ValueError('Either message_dict should have a value or provide a channel id and timestamp.')
        if message_dict is not None:
            resp = self.user.chat_delete(channel=message_dict['channel']['id'], ts=message_dict['ts'])
        else:
            resp = self.user.chat_delete(channel=channel, ts=ts)
        self._check_for_exception(resp, is_raise=True)

    def get_channel_history(self, channel: str, limit: int = 1000, latest: str = None,
                            is_raise: bool = False) -> ConversationHistory:
        """Collect channel history"""
        logger.debug(f'Getting channel history for channel {channel}.')
        resp = self.bot.conversations_history(channel=channel, limit=limit, latest=latest)
        self._check_for_exception(resp, is_raise=is_raise)
        channel_history = ConversationHistory(resp.data)

        return channel_history

    def get_thread_history(self, channel: str, ts: str, limit: int = 1000, latest: str = None,
                           is_raise: bool = False) -> ConversationReply:
        """Collect channel history"""
        logger.debug(f'Getting thread history in channel {channel} for thread at timestamp {ts}.')
        resp = self.bot.conversations_replies(channel=channel, ts=ts, limit=limit, latest=latest)
        self._check_for_exception(resp, is_raise=is_raise)
        convo_replies = ConversationReply(resp.data)

        return convo_replies

    @staticmethod
    def create_channel(channel_name: str, is_private: bool = False):
        """Creates a public/private channel"""
        logger.debug(f'Creating channel {channel_name} as a {"private" if is_private else "public"} channel')
        # TODO this

    def invite_to_channel(self, channel: str, user_list: List[str]):
        """Invites a list of users to a given channel"""
        logger.debug(f'Inviting users: {user_list} to channel {channel}')
        resp = self.bot.channels_invite(channel=channel, user=','.join(user_list))
        self._check_for_exception(resp, is_raise=True)

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
        logger.debug('Beginning query build for message search.')
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

        logger.debug(f'Sending query: {query}.')
        resp = None
        for attempt in range(3):
            resp = self.user.search_messages(
                query=query,
                count=max_results
            )
            try:
                self._check_for_exception(resp, is_raise=True)
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
        logger.debug(f'Attempting to upload file to {channel}.')
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
        self._check_for_exception(resp, is_raise=True)

    def get_emojis(self) -> Dict[str, str]:
        """Returns a dict of emojis for a given workspace"""
        resp = self.bot.emoji_list()
        self._check_for_exception(resp, is_raise=True)
        return resp['emoji']

    def get_previous_msg_in_channel(self, channel: str, timestamp: str = None) -> Optional[Message]:
        """Gets the previous message from the channel"""
        logger.debug(f'Getting previous message in channel {channel}')
        channel_history = self.get_channel_history(channel=channel, limit=10, latest=timestamp, is_raise=False)
        if channel_history.messages is not None:
            if len(channel_history.messages) > 0:
                return channel_history.messages[0]
        return None

    def get_previous_msg_in_thread(self, channel: str, timestamp: str, thread_ts: str) -> Optional[ThreadMessage]:
        """Gets the previous message from the channel"""
        logger.debug(f'Getting previous message in channel {channel} for thread at {timestamp}')
        convo_reply = self.get_thread_history(channel=channel, ts=timestamp, limit=5, latest=thread_ts, is_raise=False)
        if convo_reply.messages is not None:
            if 0 < len(convo_reply.messages) < 2:
                # Only 1 reply, which is probably the command. Return None to signal to try getting the parent instead
                return None
            elif len(convo_reply.messages) > 1:
                # Return the latest of many
                return convo_reply.messages[0]
        return None
