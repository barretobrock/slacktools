#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
import json
import string
import pygsheets
import requests
import pandas as pd
from typing import Union, List, Optional
from tabulate import tabulate
from asyncio import Future
from slack import WebClient
from slack.web.slack_response import SlackResponse
from slack.errors import SlackApiError
from random import randint
from datetime import datetime as dt
from datetime import timedelta as tdelta


class GSheetReader:
    """A class to help with reading in Google Sheets"""
    def __init__(self, sheet_key: str):
        with open(os.path.join(os.path.expanduser('~'), *['keys', 'GSHEET_READER'])) as f:
            gsheets_creds = json.loads(f.read())
        os.environ['GDRIVE_API_CREDENTIALS'] = json.dumps(gsheets_creds)
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


class BlockKitBuilder:
    """Helper class to build out Block Kit things"""

    def __init__(self):
        pass

    @staticmethod
    def make_block_section(obj: Union[str, list], join_str: str = '\n', accessory: dict = None) -> dict:
        """Returns a Block Kit dictionary containing the markdown-supported text
        Args:
            obj: str or list, the block of text to include in the section
            join_str: str, the string to join a list of strings with
            accessory: dict, any acceptable acceccory to add to the section (e.g., button)
        """
        if isinstance(obj, list):
            txt = join_str.join(obj)
        elif isinstance(obj, str):
            txt = obj
        else:
            txt = str(obj)

        section = {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': txt
            }
        }

        if accessory is not None:
            section['accessory'] = accessory

        return section

    @staticmethod
    def make_image_accessory(url: str, alt_txt: str) -> dict:
        """Builds a dict for describing an accessory image, generally used with make_block_section
        Args:
            url: str, the url that points to the image
            alt_txt: str, alt text to the image. this will be displayed on hover / for any screen readers
        """
        return {
            'type': 'image',
            'image_url': url,
            'alt_text': alt_txt
        }

    @staticmethod
    def make_block_divider() -> dict:
        """Returns a dict that renders a divider in Slack's Block Kit"""
        return {
            'type': 'divider'
        }

    @staticmethod
    def make_block_multiselect(desc: str, btn_txt: str, option_list: List[dict],
                               max_selected_items: int = None) -> dict:
        """Returns a dict that renders a multi select form in Slack's Block Kit
        Args:
            desc: str, the markdown-supported text that describes what's being selected
            btn_txt: str, text that goes inside the button element
            option_list: list of dict, options to include
                expected keys:
                    txt: option text
                    value: the value to apply to this option (returned in API)
            max_selected_items: int, if included, will establish a limit to the max number
                of selected items in the multiselect
        """

        options = []
        for x in option_list:
            options.append({
                'text': {
                    'type': 'plain_text',
                    'text': x['txt'],
                    'emoji': True
                },
                'value': x['value']
            })

        multiselect_dict = {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': desc
            },
            'accessory': {
                'type': 'multi_static_select',
                'placeholder': {
                    'type': 'plain_text',
                    'text': btn_txt,
                    'emoji': True
                },
                'options': options
            }
        }

        if max_selected_items is not None:
            multiselect_dict['accessory']['max_selected_items'] = max_selected_items
        return multiselect_dict

    @staticmethod
    def make_block_button(btn_txt: str, value: str) -> dict:
        """Returns a dict that renders a button in Slack's Block Kit"""
        return {
            'type': 'button',
            'text': {
                'type': 'plain_text',
                'text': btn_txt,
                'emoji': True
            },
            'value': value
        }

    @staticmethod
    def make_context_section(txt_obj: Union[str, List[str]]) -> dict:
        """Takes in a list of text chunks and returns a dictionary
        that renders a context section in Block Kit
        Args:
            txt_obj: list of str or str, tex to include in the context block
        """
        if isinstance(txt_obj, str):
            element_list = [{'type': 'mrkdwn', 'text': txt_obj}]
        else:
            element_list = [{'type': 'mrkdwn', 'text': x} for x in txt_obj]

        return {
            "type": "context",
            "elements": element_list
        }

    def make_button_group(self, button_list: List[dict]) -> dict:
        """Takes in a list of dicts containing button text & value,
        returns a dictionary that renders the entire set of buttons together

        Args:
            button_list: list of dict, expected keys:
                txt: the button text
                value: the value attached to the button
        """
        return {
            'type': 'actions',
            'elements': [self.make_block_button(x['txt'], x['value']) for x in button_list]
        }


class SlackTools:
    """Tools to make working with Slack API better"""

    def __init__(self, team: str, xoxp_token: str, xoxb_token: str, cookie: str = ''):
        """
        Args:
            team: str, the Slack workspace name
            xoxp_token: str, the user token
            xoxb_token: str, the bot token
            cookie: str, cookie used for special processes outside
                the realm of common API calls e.g., emoji uploads
                default: empty
        """
        self.team = team
        # Grab tokens
        self.xoxp_token = xoxp_token
        self.xoxb_token = xoxb_token
        self.cookie = cookie
        self.bkb = BlockKitBuilder()

        self.user = WebClient(xoxp_token)
        self.bot = WebClient(xoxb_token)
        # Test API calls to the bot
        self.bot_id = self.bot.auth_test()
        self.session = self._init_session() if cookie != '' else None

    @staticmethod
    def parse_tag_from_text(txt: str) -> Optional[str]:
        """Parses an <@{user}> mention and extracts the user id from it"""
        match = re.match(r'^<@(.*)>', txt)
        if match is not None:
            # IDs are stored as uppercase. This will help with matching
            return match.group(1).upper()
        return None

    def _init_session(self) -> requests.Session:
        """Initialises a session for use with special API calls not allowed through the python package"""
        base_url = 'https://{}.slack.com'.format(self.team)

        session = requests.session()
        session.headers = {'Cookie': self.cookie}
        session.url_customize = '{}/customize/emoji'.format(base_url)
        session.url_add = '{}/api/emoji.add'.format(base_url)
        session.url_list = '{}/api/emoji.adminList'.format(base_url)
        session.api_token = self.xoxp_token
        return session

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
        }

    def get_channel_members(self, channel: str, humans_only: bool = False) -> List[dict]:
        """Collect members of a particular channel
        Args:
            channel: str, the channel to examine
            humans_only: bool, if True, will only return non-bots in the channel
        """
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
        user_info = []
        for user in user_list:
            resp = None
            try:
                resp = self.bot.users_info(user=user)
            except SlackApiError:
                if throw_exception:
                    self._check_for_exception(resp)
                if resp['error'] == 'user_not_found':
                    # Unsuccessful at finding user. Add in a placeholder.
                    resp = {
                        'user': {
                            'id': user,
                            'real_name': 'Unknown User',
                            'name': 'unknown_user',
                            'display_name': 'unknown_user',
                        }
                    }
            if 'user' in resp.data.keys():
                user_info.append(resp['user'])
        return user_info

    def private_channel_message(self, user_id: str, channel: str, message: str, **kwargs):
        """Send a message to a user on the channel"""
        resp = self.bot.chat_postEphemeral(channel=channel, user=user_id, text=message, **kwargs)
        # Check response for exception
        self._check_for_exception(resp)

    def private_message(self, user_id: str, message: str, **kwargs):
        """Send private message to user"""
        # Grab the DM "channel" associated with the user
        resp = self.bot.im_open(user=user_id)
        # Check response for exception
        self._check_for_exception(resp)
        # DM the user
        self.send_message(channel=resp['channel']['id'], message=message, **kwargs)

    def get_channel_history(self, channel: str, limit: int = 1000) -> List[dict]:
        """Collect channel history"""
        resp = self.bot.conversations_history(channel=channel, limit=limit)
        self._check_for_exception(resp)
        return resp['messages']

    def send_message(self, channel: str, message: str, **kwargs):
        """Sends a message to the specific channel"""
        resp = self.bot.chat_postMessage(channel=channel, text=message, **kwargs)
        self._check_for_exception(resp)

    def upload_file(self, channel: str, filepath: str, filename: str):
        """Uploads the selected file to the given channel"""
        resp = self.bot.files_upload(file=open(filepath, 'rb'), channels=channel, filename=filename)
        self._check_for_exception(resp)

    @staticmethod
    def df_to_slack_table(df: pd.DataFrame) -> str:
        """Takes in a dataframe, outputs a string formatted for Slack"""
        return tabulate(df, headers='keys', tablefmt='github', showindex='never')

    def _upload_emoji(self, filepath: str) -> bool:
        """Uploads an emoji to the workspace
        NOTE: The name of the emoji is taken from the filepath
        """
        if self.session is None:
            raise Exception('Cannot initialize session. Session not established due to lack of cookie.')
        filename = os.path.split(filepath)[1]
        emoji_name = os.path.splitext(filename)[0]
        data = {
            'mode': 'data',
            'name': emoji_name,
            'token': self.session.api_token
        }
        files = {'image': open(filepath, 'rb')}
        r = self.session.post(self.session.url_add, data=data, files=files, allow_redirects=False)
        r.raise_for_status()

        # Slack returns 200 OK even if upload fails, so check for status.
        response_json = r.json()
        if not response_json['ok']:
            print(f"Error with uploading {emoji_name}: {response_json}")
        return response_json['ok']

    def upload_emojis(self, upload_dir: str, wait_s: int = 5, announce_channel: str = None) -> Optional[str]:
        """Uploads any .jpg .png .gif files in a given directory,
            Announces uploads to channel, if announce=True

        Methods
             - Scan in files from directory
             - clean emoji name from file path
             - build dict: key = emoji name, value = filepath
        """
        existing_emojis = [k for k, v in self.get_emojis().items()]

        emoji_dict = {}
        for file in os.listdir(upload_dir):
            file_split = os.path.splitext(file)
            if file_split[1] in ['.png', '.jpg', '.gif']:
                filepath = os.path.join(upload_dir, file)
                emoji_name = file_split[0]
                if emoji_name not in existing_emojis:
                    emoji_dict[emoji_name] = filepath

        successfully_uploaded = []
        for k, v in emoji_dict.items():
            if k in successfully_uploaded:
                continue
            successful = self._upload_emoji(v)
            if successful:
                successfully_uploaded.append(k)
            # Wait
            print(':{}: successful - {:.2%} done'.format(k, len(successfully_uploaded) / len(emoji_dict)))
            time.sleep(wait_s)

        if announce_channel is not None:
            # Report the emojis captured to the channel
            # 30 emojis per line, 5 lines per post
            out_str = '\n'
            cnt = 0
            for item in successfully_uploaded:
                out_str += ':{}:'.format(item)
                cnt += 1
                if cnt % 30 == 0:
                    out_str += '\n'
                if cnt == 150:
                    self.send_message(announce_channel, out_str)
                    out_str = '\n'
                    cnt = 0
            if cnt > 0:
                self.send_message(announce_channel, out_str)
            return out_str
        return None

    @staticmethod
    def download_emojis(emoji_dict: dict, download_dir: str):
        """Downloads a dict of emojis
        NOTE: key = emoji name, value = url or data
        """
        for k, v in emoji_dict.items():
            if v[:4] == 'data':
                data = v
            elif v[:4] == 'http':
                r = requests.get(v)
                data = r.content
            else:
                continue
            # Write pic to file
            fname = '{}{}'.format(k, os.path.splitext(v)[1])
            fpath = os.path.join(download_dir, fname)
            write = 'wb' if isinstance(data, bytes) else 'w'
            with open(fpath, write) as f:
                f.write(data)

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

    def delete_message(self, message_dict: dict):
        """Deletes a given message
        NOTE: Since messages are deleted by channel id and timestamp, it's recommended to
            use search_messages_by_date() to determine the messages to delete
        """
        resp = self.bot.chat_delete(channel=message_dict['channel']['id'], ts=message_dict['ts'])
        self._check_for_exception(resp)

    def search_messages_by_date(self, channel: str, from_date: str, date_format: str = '%Y-%m-%d %H:%M',
                                max_results: int = 100) -> Optional[List[dict]]:
        """Search for messages in a channel after a certain date

        Args:
            channel: str, the channel (e.g., "#channel")
            from_date: str, the date from which to begin collecting channels
            date_format: str, the format of the date entered
            max_results: int, the maximum number of results per page to return

        Returns: list of dict, channels matching the query
        """
        from_date = dt.strptime(from_date, date_format)
        # using the 'after' filter here, so take it back one day
        slack_date = from_date - tdelta(days=1)

        resp = None
        for attempt in range(3):
            resp = self.user.search_messages(
                query=f'in:{channel} after:{slack_date:%F}',
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
            filtered_msgs = []
            for msg in msgs:
                # Append the message as long as it's timestamp is later or equal to the time entered
                ts = dt.fromtimestamp(int(round(float(msg['ts']), 0)))
                if ts >= from_date:
                    filtered_msgs.append(msg)
            return filtered_msgs

        return None

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

    @staticmethod
    def read_in_sheets(sheet_key: str) -> dict:
        """Reads in GSheets for Viktor"""
        gs = GSheetReader(sheet_key)
        sheets = gs.sheets
        ws_dict = {}
        for sheet in sheets:
            ws_dict.update({
                sheet.title: gs.get_sheet(sheet.title)
            })
        return ws_dict

    @staticmethod
    def write_sheet(sheet_key: str, sheet_name: str, df: pd.DataFrame):
        gs = GSheetReader(sheet_key)
        gs.write_df_to_sheet(sheet_key, sheet_name, df)
