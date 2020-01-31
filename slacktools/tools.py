#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
import string
import signal
import requests
from tabulate import tabulate
from slack import WebClient
from random import randint
from datetime import datetime as dt
from datetime import timedelta as tdelta
from kavalkilu import GSheetReader, Log


class SlackTools:
    """Tools to make working with Slack better"""

    def __init__(self, log_name, triggers, team, xoxp_token, xoxb_token, cookie=''):
        """
        :param log_name: str, log name of kavalkilu.Log object for logging special events
        :param triggers: list of str, any specific text trigger to kick off the bot's processing of commands
            default: None. (i.e., will only trigger on @mentions)
        :param team: str, the Slack workspace name
        :param xoxp_token: str, the user token
        :param xoxb_token: str, the bot token
        :param cookie: str, cookie used for special processes outside the realm of common API calls
            e.g., emoji uploads
            default: empty
        """
        self.log = Log(log_name, child_name='slacktools')
        # Enforce lowercase triggers (regex will be indifferent to case anyway
        if triggers is not None:
            triggers = list(map(str.lower, triggers))

        # Set triggers to @bot and any custom text
        trigger_formatted = '|{}'.format('|'.join(triggers)) if triggers is not None else ''
        self.MENTION_REGEX = r'^(<@(|[WU].+?)>{})(.*)'.format(trigger_formatted)
        self.team = team
        # Grab tokens
        self.xoxp_token = xoxp_token
        self.xoxb_token = xoxb_token
        self.cookie = cookie

        self.user = WebClient(xoxp_token)
        self.bot = WebClient(xoxb_token)
        self.bot_id = self.bot.auth_test()
        # self.bot_id = self.bot.api_call('auth.test')['user_id']
        self.triggers = [self.bot_id]
        if triggers is not None:
            # Add in custom text triggers, if any
            self.triggers += triggers
        self.session = self._init_session() if cookie != '' else None

    def parse_direct_mention(self, message):
        """Parses user and other text from direct mention"""
        matches = re.search(self.MENTION_REGEX, message, re.IGNORECASE)
        if matches is not None:
            if matches.group(1).lower() in self.triggers:
                # Matched using abbreviated triggers
                trigger = matches.group(1).lower()
                self.log.debug('Matched on abbreviated trigger: {}'.format(trigger))
            else:
                # Matched using bot id
                trigger = matches.group(2)
                self.log.debug('Matched on bot id: {}'.format(trigger))
            message_txt = matches.group(3).lower().strip()
            raw_message = matches.group(3).strip()
            self.log.debug('Message: {}'.format(message_txt))
            return trigger, message_txt, raw_message
        return None, None, None

    def parse_bot_commands(self, slack_events):
        """Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event['type'] == 'message' and "subtype" not in event:
                trigger, message, raw_message = self.parse_direct_mention(event['text'])
                if trigger in self.triggers:
                    return {
                        'user': event['user'],
                        'channel': event['channel'],
                        'message': message.strip(),
                        'raw_message': raw_message.strip()
                    }
        return None

    @staticmethod
    def parse_tag_from_text(txt):
        """Parses an <@{user}> mention and extracts the user id from it"""
        match = re.match(r'^<@(.*)>', txt)
        if match is not None:
            # IDs are stored as uppercase. This will help with matching
            return match.group(1).upper()
        return None

    def _init_session(self):
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
    def _check_for_exception(response):
        """Checks API response for exception info.
        If error, will return error message and any additional info
        """
        if not response['ok']:
            # Error occurred
            err_msg = response['error']
            if err_msg == 'missing_scope':
                err_msg += '\nneeded: {needed}\n'.format(**response)
            raise Exception(err_msg)

    def get_channel_members(self, channel, humans_only=False):
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
            users.append({
                'id': user['id'],
                'name': user['name'],
                'real_name': user['real_name'],
                'is_bot': user['is_bot'],
                'display_name': user['profile']['display_name'],
            })

        return [user for user in users if not user['is_bot']] if humans_only else users

    def get_users_info(self, user_list):
        """Collects info from a list of user ids"""
        user_info = []
        for user in user_list:
            resp = self.bot.users_info(user=user)
            self._check_for_exception(resp)
            user_info.append(resp['user'])
        return user_info

    def private_channel_message(self, user_id, channel, message):
        """Send a message to a user on the channel"""
        resp = self.bot.chat_postEphemeral(channel=channel, user=user_id, text=message)
        # Check response for exception
        self._check_for_exception(resp)

    def private_message(self, user_id, message):
        """Send private message to user"""
        # Grab the DM "channel" associated with the user
        resp = self.bot.im_open(user=user_id)
        # Check response for exception
        self._check_for_exception(resp)
        # DM the user
        self.send_message(channel=resp['channel']['id'], message=message)

    def get_channel_history(self, channel, limit=1000):
        """Collect channel history"""
        resp = self.bot.channels_history(channel=channel, limit=limit)
        self._check_for_exception(resp)
        return resp['messages']

    def send_message(self, channel, message):
        """Sends a message to the specific channel"""
        resp = self.bot.chat_postMessage(channel=channel, text=message)
        self._check_for_exception(resp)

    def upload_file(self, channel, filepath, filename):
        """Uploads the selected file to the given channel"""
        resp = self.bot.files_upload(file=open(filepath, 'rb'), channels=channel, filename=filename)
        self._check_for_exception(resp)

    @staticmethod
    def df_to_slack_table(df):
        """Takes in a dataframe, outputs a string formatted for Slack"""
        return tabulate(df, headers='keys', tablefmt='github', showindex='never')

    def _upload_emoji(self, filepath):
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
            print("Error with uploading {}: {}".format(emoji_name, response_json))
        return response_json['ok']

    def upload_emojis(self, upload_dir, announce=True, wait_s=5):
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

        if announce:
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
                    self.send_message('emoji_suggestions', out_str)
                    out_str = '\n'
                    cnt = 0
            if cnt > 0:
                self.send_message('emoji_suggestions', out_str)
            return out_str
        return None

    @staticmethod
    def download_emojis(emoji_dict, download_dir):
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
    def _exact_match_emojis(emoji_dict, exact_match_list):
        """Matches emojis exactly"""
        matches = {}
        for k, v in emoji_dict.items():
            if k in exact_match_list:
                matches[k] = v
        return matches

    @staticmethod
    def _fuzzy_match_emojis(emoji_dict, fuzzy_match):
        """Fuzzy matches emojis"""
        matches = {}
        pattern = re.compile(fuzzy_match, re.IGNORECASE)
        for k, v in emoji_dict.items():
            if pattern.match(k) is not None:
                matches[k] = v
        return matches

    def match_emojis(self, exact_match_list=None, fuzzy_match=None):
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

    def get_emojis(self):
        """Returns a dict of emojis for a given workspace"""
        resp = self.bot.emoji_list()
        self._check_for_exception(resp)
        return resp['emoji']

    def delete_message(self, message_dict):
        """Deletes a given message
        NOTE: Since messages are deleted by channel id and timestamp, it's recommended to
            use search_messages_by_date() to determine the messages to delete
        """
        resp = self.bot.chat_delete(channel=message_dict['channel']['id'], ts=message_dict['ts'])
        self._check_for_exception(resp)

    def search_messages_by_date(self, channel, from_date, date_format='%Y-%m-%d %H:%M', max_results=100):
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

        for attempt in range(3):
            resp = self.user.api_call(
                'search.messages',
                query='in:{} after:{:%F}'.format(channel, slack_date),
                count=max_results
            )
            try:
                self._check_for_exception(resp)
                break
            except Exception as e:
                print('Call failed. Error: {}'.format(e))
                time.sleep(2)

        if 'messages' in resp.keys():
            msgs = resp['messages']['matches']
            filtered_msgs = []
            for msg in msgs:
                # Append the message as long as it's timestamp is later or equal to the time entered
                ts = dt.fromtimestamp(int(round(float(msg['ts']), 0)))
                if ts >= from_date:
                    filtered_msgs.append(msg)
            return filtered_msgs

        return None

    def _build_emoji_letter_dict(self):
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

    def build_phrase(self, phrase):
        """Build your awesome phrase"""

        letter_dict = self._build_emoji_letter_dict()
        built_phrase = []
        for l in list(phrase):
            # Lookup letter
            if l in letter_dict.keys():
                vals = letter_dict[l]
                rand_l = vals[randint(0, len(vals) - 1)]
                built_phrase.append(':{}:'.format(rand_l))
            elif l == ' ':
                built_phrase.append(':blank:')
            else:
                built_phrase.append(l)

        done_phrase = ''.join(built_phrase)
        return done_phrase

    def read_in_sheets(self, sheet_key):
        """Reads in GSheets for Viktor"""
        gs = GSheetReader(sheet_key)
        sheets = gs.sheets
        ws_dict = {}
        for sheet in sheets:
            ws_dict.update({
                sheet.title: gs.get_sheet(sheet.title)
            })
        return ws_dict

