#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
import json
import string
from types import SimpleNamespace
import pygsheets
import requests
from io import BytesIO
import pandas as pd
from typing import Union, List, Optional, Tuple, Dict
from tabulate import tabulate
from asyncio import Future
from slack import WebClient
from slack.web.slack_response import SlackResponse
from slack.errors import SlackApiError
from random import randint
from datetime import datetime as dt
from datetime import timedelta as tdelta
from easylogger import Log
from pykeepass import PyKeePass
from pykeepass.entry import Entry
from .block_kit import BlockKitBuilder
from .slacksession import SlackSession


class SecretStore:
    KEY_DIR = os.path.join(os.path.expanduser('~'), 'keys')
    DEFAULT_FILE_NAME = 'secretprops.kdbx'
    DEFAULT_PASSWORD_FILE = 'SECRETPROP'

    def __init__(self, fname: str = DEFAULT_FILE_NAME, password: str = None,
                 password_fname: str = DEFAULT_PASSWORD_FILE):
        self.db = None

        if password_fname is not None and password is None:
            with open(os.path.join(self.KEY_DIR, password_fname)) as f:
                password = f.read().strip()
        # Read in the database
        self.load_database(fname, password)

    def load_database(self, fname: str, password: str):
        self.db = PyKeePass(os.path.join(self.KEY_DIR, fname), password=password)

    def get_entry(self, entry_name: str) -> Entry:
        return self.db.find_entries(title=entry_name, first=True)

    def get_key(self, key_name: str) -> Dict:
        entry = self.get_entry(key_name)
        if entry is None:
            return {}
        if any([x is not None for x in [entry.username, entry.password]]):
            resp = {
                'un': entry.username,
                'pw': entry.password
            }
        else:
            resp = {}
        if len(entry.attachments) > 0:
            for att in entry.attachments:
                # For attachments, try to decode any that we might expect. For now, that's just JSON
                if isinstance(att.data, bytes):
                    # Decode to string, try loading as json
                    try:
                        file_contents = json.loads(att.data.decode('utf-8'))
                        resp.update(file_contents)
                    except:
                        resp[att.filename] = att.data.decode('utf-8')
        resp.update(entry.custom_properties)
        return resp

    def get_key_and_make_ns(self, entry: str) -> SimpleNamespace:
        entry_dict = self.get_key(entry)
        processed_dict = {}
        for k, v in entry_dict.items():
            processed_dict[k.replace('-', '_')] = v
        return SimpleNamespace(**processed_dict)


class GSheetReader:
    """A class to help with reading in Google Sheets"""
    def __init__(self, sec_store: SecretStore, sheet_key: str):
        creds = sec_store.get_key('gsheet-reader')
        os.environ['GDRIVE_API_CREDENTIALS'] = json.dumps(creds)
        self.gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')
        self.sheets = self.gc.open_by_key(sheet_key).worksheets()

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Retrieves a sheet as a pandas dataframe"""
        for sheet in self.sheets:
            if sheet.title == sheet_name:
                return sheet.get_as_df()
        raise ValueError(f'The sheet name "{sheet_name}" was not found '
                         f'in the list of available sheets: ({",".join([x.title for x in self.sheets])})')

    def write_df_to_sheet(self, sheet_key: str, sheet_name: str, df: pd.DataFrame):
        """Write df to sheet"""
        wb = self.gc.open_by_key(sheet_key)
        sheet = wb.worksheet_by_title(sheet_name)
        sheet.clear()
        sheet.set_dataframe(df, (1, 1))


class SlackTools:
    """Tools to make working with Slack API better"""

    def __init__(self, credstore: SecretStore, slack_cred_name: str, parent_log: Log, use_session: bool = False):
        """
        Args:
            credstore: SecretStore, contains tokens & other secrets for connecting & interacting with Slack
                required keys:
                    team: str, the Slack workspace name
                    xoxp-token: str, the user token
                    xoxb-token: str, the bot token
                optional keys:
                    cookie: str, cookie used for special processes outside
                        the realm of common API calls e.g., emoji uploads
            parent_log: the parent log to attach to.
            use_session: enable when looking to do things like upload new emojis
        """
        self.log = Log(parent_log, child_name=self.__class__.__name__)
        slack_creds = credstore.get_key_and_make_ns(slack_cred_name)
        # Determine if a valid sheet key was provided. If not, just don't instantiate a gsr object
        try:
            sheet_key = slack_creds.spreadsheet_key
            self.gsr = GSheetReader(sec_store=credstore, sheet_key=sheet_key)
        except AttributeError:
            self.gsr = None
        self.team = slack_creds.team
        # Grab tokens
        self.xoxp_token = slack_creds.xoxp_token
        self.xoxb_token = slack_creds.xoxb_token
        try:
            self.cookie = slack_creds.cookie
        except AttributeError:
            self.cookie = ''

        self.bkb = BlockKitBuilder()

        self.user = WebClient(self.xoxp_token)
        self.bot = WebClient(self.xoxb_token)
        # Test API calls to the bot
        self.bot_id = self.bot.auth_test()

        self.session = SlackSession(self.team, self.cookie, parent_log=self.log) if use_session else None

    @staticmethod
    def parse_tag_from_text(txt: str) -> Optional[str]:
        """Parses an <@{user}> mention and extracts the user id from it"""
        match = re.match(r'^<@(.*)>', txt)
        if match is not None:
            # IDs are stored as uppercase. This will help with matching
            return match.group(1).upper()
        return None

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
        self.log.debug(f'Collecting users\' info.')
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

    def search_messages_by_date(self, channel: str = None, from_uid: str = None, after_date: dt = None,
                                after_ts: dt = None, on_date: dt = None, during_m: dt = None,
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
        self.log.debug(f'Beginning query build for message search.')
        slack_date_fmt = '%m-%d-%Y'  # Slack has a specific format to adhere to when in the US lol
        # Begin building queries
        query = ''
        if channel is not None:
            query += f'in:{channel}'
        if from_uid is not None:
            query += f' from:<@{from_uid}>'

        if after_date is not None:
            # Made this inclusive to avoid excluding the entire date
            query += f' after:{(after_date - tdelta(days=1)).strftime(slack_date_fmt)}'
        elif on_date is not None:
            query += f' on:{on_date.strftime(slack_date_fmt)}'
        elif during_m is not None:
            query += f' during:{during_m.strftime("%B").lower()}'
        if has_emoji is not None:
            query += f' has:{has_emoji}'
        if has_pin is not None:
            if has_pin:
                query += f' has:pin'

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

    @staticmethod
    def df_to_slack_table(df: pd.DataFrame) -> str:
        """Takes in a dataframe, outputs a string formatted for Slack"""
        return tabulate(df, headers='keys', tablefmt='github', showindex='never')

    @staticmethod
    def _exact_match_emojis(emoji_dict: dict, exact_match_list: List[str]) -> dict:
        """Matches emojis exactly"""
        matches = {}
        for k, v in emoji_dict.items():
            if k in exact_match_list:
                matches[k] = v
        return matches

    @staticmethod
    def _fuzzy_match_emojis(emoji_dict: dict, fuzzy_match: str) -> dict:
        """Fuzzy matches emojis"""
        matches = {}
        pattern = re.compile(fuzzy_match, re.IGNORECASE)
        for k, v in emoji_dict.items():
            if pattern.match(k) is not None:
                matches[k] = v
        return matches

    def match_emojis(self, exact_match_list: List[str] = None, fuzzy_match: str = None) -> dict:
        """Matches emojis in a workspace either by passing in an exact list or fuzzy-match (regex) list"""
        emoji_dict = self.get_emojis()

        matches = {}
        # Exact matches
        if exact_match_list is not None:
            exact_matches = self._exact_match_emojis(emoji_dict, exact_match_list)
            matches.update(exact_matches)
        # Fuzzy matches
        if fuzzy_match is not None:
            fuzzy_matches = self._fuzzy_match_emojis(emoji_dict, fuzzy_match)
            matches.update(fuzzy_matches)
        return matches

    def get_emojis(self) -> dict:
        """Returns a dict of emojis for a given workspace"""
        resp = self.bot.emoji_list()
        self._check_for_exception(resp)
        return resp['emoji']

    @staticmethod
    def _build_emoji_letter_dict() -> dict:
        """Sets up use of replacing words with slack emojis"""
        a2z = string.ascii_lowercase
        letter_grp = [
            'regional_indicator_',
            'letter-',
            'scrabble-'
        ]

        grp = [['{}{}'.format(y, x) for x in a2z] for y in letter_grp]

        letter_dict = {}

        for i, ltr in enumerate(list(a2z)):
            ltr_list = []
            for g in grp:
                ltr_list.append(g[i])

            letter_dict[ltr] = ltr_list

        # Additional, irregular entries
        addl = {
            'a': ['amazon', 'a', 'slayer_a', 'a_'],
            'b': ['b'],
            'e': ['slayer_e'],
            'l': ['slayer_l'],
            'm': ['m'],
            'o': ['o'],
            'r': ['slayer_r'],
            's': ['s', 'slayer_s'],
            'x': ['x'],
            'y': ['slayer_y'],
            'z': ['zabbix'],
            '.': ['dotdotdot-intensifies', 'period'],
            '!': ['exclamation', 'heavy_heart_exclamation_mark_ornament', 'grey_exclamation'],
            '?': ['question', 'grey_question', 'questionman', 'question_block'],
            '"': ['airquotes-start', 'airquotes-end'],
            "'": ['airquotes-start', 'airquotes-end'],
        }

        for k, v in addl.items():
            if k in letter_dict.keys():
                letter_dict[k] = letter_dict[k] + v
            else:
                letter_dict[k] = v
        return letter_dict

    def build_phrase(self, phrase: str) -> str:
        """Build your awesome phrase"""

        letter_dict = self._build_emoji_letter_dict()
        built_phrase = []
        for letter in list(phrase):
            # Lookup letter
            if letter in letter_dict.keys():
                vals = letter_dict[letter]
                rand_l = vals[randint(0, len(vals) - 1)]
                built_phrase.append(':{}:'.format(rand_l))
            elif letter == ' ':
                built_phrase.append(':blank:')
            else:
                built_phrase.append(letter)

        done_phrase = ''.join(built_phrase)
        return done_phrase

    def read_in_sheets(self) -> dict:
        """Reads in GSheets"""
        sheets = self.gsr.sheets
        ws_dict = {}
        for sheet in sheets:
            ws_dict.update({
                sheet.title: self.gsr.get_sheet(sheet.title)
            })
        return ws_dict

    def write_sheet(self, sheet_key: str, sheet_name: str, df: pd.DataFrame):
        self.gsr.write_df_to_sheet(sheet_key, sheet_name, df)
