#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta as reldelta
from typing import List, Union, Tuple, Optional, Callable
from .tools import BlockKitBuilder, SlackTools


class SlackBotBase(SlackTools):
    """The base class for an interactive bot in Slack"""
    def __init__(self, log_name: str, triggers: List[str], team: str, main_channel: str, xoxp_token: str,
                 xoxb_token: str, commands: dict, cmd_categories: List[str]):
        """
        Args:
            log_name: str, log name of kavalkilu.Log object for logging special events
            triggers: list of str, any specific text trigger to kick off the bot's processing of commands
                default: None. (i.e., will only trigger on @mentions)
            team: str, the Slack workspace name
            main_channel: str, the default channel to communicate messages to
            xoxp_token: str, the user token
            xoxb_token: str, the bot token
            commands: dict, all the commands the bot recognizes (to be built into help text)
                expected keys:
                    cat: str, the category of the command (for grouping purposes) - must match with categories list
                    desc: str, description of the command
                    value: str or list of func & str, the object to return / command to run
                optional keys:
                    pattern: str, the human-readable match pattern to show end users
                    flags: list of dict, shows optional flags to include int he command and what they do
                        expected keys:
                            pattern: str, the flag pattern
                            desc: str, the description of this flag
            cmd_categories: list of str, the categories to group the above commands in to
        """
        super().__init__(team, xoxp_token=xoxp_token, xoxb_token=xoxb_token)
        # self.log = Log(log_name, child_name='slacktools')
        # Enforce lowercase triggers (regex will be indifferent to case anyway
        if triggers is not None:
            triggers = list(map(str.lower, triggers))

        # Set triggers to @bot and any custom text
        trigger_formatted = '|{}'.format('|'.join(triggers)) if triggers is not None else ''
        self.MENTION_REGEX = r'^(<@(|[WU].+?)>{})(.*)'.format(trigger_formatted)
        self.main_channel = main_channel

        self.bkb = BlockKitBuilder()
        self.commands = commands
        self.cmd_categories = cmd_categories

        self.bot_id = self.bot.auth_test()
        self.triggers = [self.bot_id]
        if triggers is not None:
            # Add in custom text triggers, if any
            self.triggers += triggers

    def update_commands(self, commands: dict):
        """Updates the dictionary of commands"""
        self.commands = commands

    def build_help_block(self, intro: str, avi_url: str, avi_alt: str) -> List[dict]:
        """Builds bot's description of functions into a giant wall of help text
        Args:
            intro: str, The bot's introduction
            avi_url: str, the url to the image to display next to the intro
            avi_alt: str, alt text for the avatar

        Returns:
            list of dict, Block Kit-ready help text
        """

        blocks = [
            self.bkb.make_block_section(intro, accessory=self.bkb.make_image_accessory(avi_url, avi_alt)),
            self.bkb.make_block_divider()
        ]
        help_dict = {cat: [] for cat in self.cmd_categories}

        for k, v in self.commands.items():
            if 'pattern' not in v.keys():
                v['pattern'] = k
            if 'flags' in v.keys():
                extra_desc = '\n\t\t'.join([f'*`{x["pattern"]}`*: {x["desc"]}' for x in v['flags']])
                # Append flags to the end of the description (they'll be tabbed in)
                v["desc"] += f'\n\t_optional flags_\n\t\t{extra_desc}'
            help_dict[v['cat']].append(f'- *`{v["pattern"]}`*: {v["desc"]}')

        command_frags = []
        for k, v in help_dict.items():
            list_of_cmds = "\n".join(v)
            command_frags.append(f'*{k.title()} Commands*:\n{list_of_cmds}')

        for command in command_frags:
            blocks += [
                self.bkb.make_block_section(command),
                self.bkb.make_block_divider()
            ]

        return blocks

    def parse_direct_mention(self, message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parses user and other text from direct mention"""
        matches = re.search(self.MENTION_REGEX, message, re.IGNORECASE)
        if matches is not None:
            if matches.group(1).lower() in self.triggers:
                # Matched using abbreviated triggers
                trigger = matches.group(1).lower()
                # self.log.debug('Matched on abbreviated trigger: {}'.format(trigger))
            else:
                # Matched using bot id
                trigger = matches.group(2)
                # self.log.debug('Matched on bot id: {}'.format(trigger))
            message_txt = matches.group(3).lower().strip()
            raw_message = matches.group(3).strip()
            # self.log.debug('Message: {}'.format(message_txt))
            return trigger, message_txt, raw_message
        return None, None, None

    def parse_bot_commands(self, slack_events: List[dict]) -> Optional[dict]:
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
    def parse_flags_from_command(message: str) -> dict:
        """Takes in a message string and parses out flags in the string and the values following them
        Args:
            message: str, the command message containing the flags

        Returns:
            dict, flags parsed out into keys

        Example:
            >>> msg = 'process this command -l -u this that other --p 1 2 3 4 5'
            >>> #parse_flags_from_command(msg)
            >>> {
            >>>     'cmd': 'process this command',
            >>>     'l': '',
            >>>     'u': 'this that other',
            >>>     'p': '1 2 3 4 5'
            >>> }
        """
        msg_split = message.split(' ')
        cmd_dict = {'cmd': re.split(r'-+\w+', message)[0].strip()}
        flag_regex = re.compile(r'^-+(\w+)')
        for i, part in enumerate(msg_split):
            if flag_regex.match(part) is not None:
                flag = flag_regex.match(part).group(1)
                # Get list of values after the flag up until the next flag
                vals = []
                for val in msg_split[i + 1:]:
                    if flag_regex.match(val) is not None:
                        break
                    vals.append(val)
                cmd_dict[flag] = ' '.join(vals)
        return cmd_dict

    def get_flag_from_command(self, cmd: str, flags: Union[str, List[str]], default: Optional[str] = None) -> str:
        """Reads in the command, if no flag, will return the default
        Args:
            cmd: str, the command message to parse
            flags: str or list of str, the flag(s) to search for
            default: str, the default value to set if no flag is found
        """

        # Parse the command into a dictionary of the command parts (command, flags)
        parsed_cmd = self.parse_flags_from_command(cmd)
        if isinstance(flags, str):
            # Put this into a list to unify our examination methods
            flags = [flags]

        for flag in flags:
            if flag in parsed_cmd.keys():
                return parsed_cmd[flag]
        return default

    def handle_command(self, event_dict: dict):
        """Handles a bot command if it's known"""
        response = None
        message = event_dict['message']
        channel = event_dict['channel']

        is_matched = False
        for regex, resp_dict in self.commands.items():
            match = re.match(regex, message)
            if match is not None:
                # We've matched on a command
                resp = resp_dict['value']
                if isinstance(resp, list):
                    if isinstance(resp[0], dict):
                        # Response is a JSON blob for handling in Block Kit.
                        response = resp
                    else:
                        # Copy the list to ensure changes aren't propagated to the command list
                        resp_list = resp.copy()
                        # Examine list, replace any known strings ('message', 'channel', etc.)
                        #   with event context variables
                        for k, v in event_dict.items():
                            if k in resp_list:
                                resp_list[resp_list.index(k)] = v
                        # Function with args; sometimes response can be None
                        response = self.call_command(*resp_list, match_pattern=regex)
                else:
                    # String response
                    response = resp
                is_matched = True
                break

        if message != '' and not is_matched:
            response = f"I didn\'t understand this: *`{message}`*\n" \
                       f"Use {' or '.join([f'`{x} help`' for x in self.triggers])} to get a list of my commands."

        if response is not None:
            if isinstance(response, str):
                try:
                    response = response.format(**event_dict)
                except KeyError:
                    # Response likely has some curly braces in it that disrupt str.format().
                    # Pass string without formatting
                    pass
                self.send_message(channel, response)
            elif isinstance(response, list):
                self.send_message(channel, '', blocks=response)

    @staticmethod
    def call_command(cmd: Callable, *args, **kwargs):
        """
        Calls the command referenced while passing in arguments
        :return: None or string
        """
        return cmd(*args, **kwargs)

    @staticmethod
    def _human_readable(reldelta_val: reldelta) -> str:
        """Takes in a relative delta and makes it human readable"""
        attrs = {
            'years': 'y',
            'months': 'mo',
            'days': 'd',
            'hours': 'h',
            'minutes': 'm',
            'seconds': 's'
        }

        result_list = []
        for attr in attrs.keys():
            attr_val = getattr(reldelta_val, attr)
            if attr_val is not None:
                if attr_val > 1:
                    result_list.append('{:d}{}'.format(attr_val, attrs[attr]))
        return ' '.join(result_list)

    def get_time_elapsed(self, st_dt: datetime) -> str:
        """Gets elapsed time between two datetimes"""
        datediff = reldelta(datetime.now(), st_dt)
        return self._human_readable(datediff)

    def get_prev_msg_in_channel(self, channel: str, timestamp: str) -> Optional[str]:
        """Gets the previous message from the channel"""
        resp = self.bot.conversations_history(
            channel=channel,
            latest=timestamp,
            limit=10)
        if not resp['ok']:
            return None
        if 'messages' in resp.data.keys():
            msgs = resp['messages']
            return msgs[0]['text']
        return None

    def message_main_channel(self, message: str = None, blocks: Optional[List[dict]] = None):
        """Wrapper to send message to whole channel"""
        if message is not None:
            self.send_message(self.main_channel, message)
        elif blocks is not None:
            self.send_message(self.main_channel, message='', blocks=blocks)
        else:
            raise ValueError('No data passed for message.')
