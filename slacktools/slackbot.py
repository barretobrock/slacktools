#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import traceback
from datetime import datetime
from dateutil import relativedelta
from types import SimpleNamespace
from typing import (
    Dict,
    List,
    Union,
    Tuple,
    Optional,
    Callable
)
from loguru import logger
from slacktools.tools import SlackTools
from slacktools.block_kit import BlockKitBuilder as BKitB
from slacktools.slack_input_parser import block_text_converter


class SlackBotBase(SlackTools):
    """The base class for an interactive bot in Slack"""
    def __init__(self, bot_cred_entry: SimpleNamespace, triggers: List[str],
                 main_channel: str, debug: bool = False, parent_log: logger = None, use_session: bool = False):
        """
        Args:
            triggers: list of str, any specific text trigger to kick off the bot's processing of commands
                default: None. (i.e., will only trigger on @mentions)
            bot_cred_entry: SimpleNamespace, contains tokens & other secrets for connecting &
                    interacting with Slack
                required keys:
                    team: str, the Slack workspace name
                    xoxp-token: str, the user token
                    xoxb-token: str, the bot token
                optional keys:
                    d-cookie: str, cookie used for special processes outside
                        the realm of common API calls e.g., emoji uploads
                    xoxc-token: str, token for uploading emojis
            main_channel: str, the channel to send messages by default
            debug: bool, if True, will provide additional info into exceptions
        """
        self._log = parent_log.bind(child_name=self.__class__.__name__)
        super().__init__(bot_cred_entry=bot_cred_entry, parent_log=self._log, use_session=use_session)
        self.debug = debug
        # Enforce lowercase triggers (regex will be indifferent to case anyway
        if triggers is not None:
            triggers = list(map(str.lower, triggers))

        # Set triggers to @bot and any custom text
        trigger_formatted = '|{}'.format('|'.join(triggers)) if triggers is not None else ''
        self.MENTION_REGEX = r'^(<@(|[WU].+?)>{})([.\s\S ]*)'.format(trigger_formatted)
        self.main_channel = main_channel

        self.commands = []

        self.triggers = [f'{self.user_id}']
        # User ids are formatted in a different way, so just
        #   break this out into a variable for displaying in help text
        self.triggers_txt = [f'<@{self.user_id}>']
        if triggers is not None:
            # Add in custom text triggers, if any
            self.triggers += triggers
            self.triggers_txt += triggers

        # This is a data store of handled past message hashes to help enforce only one action per command issued
        #   This was mainly built as a response to occasional duplicate responses
        #   due to delay in Slack receiving a response. I've yet to figure out how to improve response time
        self.message_events = []

    def update_commands(self, commands: List[Dict[str, Union[str, List[str], Callable]]]):
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
        self._log.debug('Building help block')
        blocks = [
            BKitB.make_block_section(intro, accessory=BKitB.make_image_element(avi_url, avi_alt)),
            BKitB.make_block_divider()
        ]
        groups = list(set([c.get('group') for c in self.commands]))
        help_dict = {group: [] for group in groups}

        for cmd_dict in self.commands:
            pattern = cmd_dict.get('pattern')
            group = cmd_dict.get('group')
            desc = cmd_dict.get('desc')
            flags = cmd_dict.get('flags')
            if flags is not None:
                extra_desc = '\n\t\t'.join([f'*`{x}`*' for x in flags])
                # Append flags to the end of the description (they'll be tabbed in)
                desc += f'\n\t_optional flags_\n\t\t{extra_desc}'
            help_dict[group].append(f' \t*`{pattern}`*: {desc}')

        command_frags = []
        for k, v in help_dict.items():
            list_of_cmds = "\n".join(v)
            command_frags.append(f'*{k.title()} Commands*:\n{list_of_cmds}')

        for command in command_frags:
            blocks += [
                BKitB.make_block_section(command),
                BKitB.make_block_divider()
            ]

        return blocks

    def parse_direct_mention(self, message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parses user and other text from direct mention"""
        matches = re.search(self.MENTION_REGEX, message, re.IGNORECASE)
        if matches is not None:
            if matches.group(1).lower() in self.triggers:
                # Matched using abbreviated triggers
                trigger = matches.group(1).lower()
                self._log.debug(f'Matched on abbreviated trigger: {trigger}, msg: {message}')
            else:
                # Matched using bot id
                trigger = matches.group(2)
                self._log.debug(f'Matched on bot id: {trigger}, msg: {message}')
            message_txt = matches.group(3).lower().strip()
            raw_message = matches.group(3).strip()
            # self.log.debug('Message: {}'.format(message_txt))
            return trigger, message_txt, raw_message
        return None, None, None

    def parse_event(self, event_data: dict):
        """Takes in an Events API message-triggered event dict and determines
         if a command was issued to the bot"""
        event = event_data['event']
        msg_packet = None
        if event['type'] == 'message' and "subtype" not in event:
            trigger, message, raw_message = self.parse_direct_mention(event['text'])
            if trigger in self.triggers:
                # Build a message hash
                msg_hash = f'{event["channel"]}_{event["ts"]}'
                if msg_hash not in self.message_events:
                    self.message_events.append(msg_hash)
                    msg_packet = {
                        'message': message.strip(),
                        'raw_message': raw_message.strip()
                    }
                    # Add in all the other stuff
                    msg_packet.update(event)

        if msg_packet is not None:
            try:
                self.handle_command(msg_packet)
            except Exception as e:
                if not isinstance(e, RuntimeError):
                    exception_msg = '{}: {}'.format(e.__class__.__name__, e)
                    if self.debug:
                        blocks = [
                            BKitB.make_context_section([
                                BKitB.markdown_section(f"Exception occurred: \n*`{exception_msg}`*")
                            ]),
                            BKitB.make_block_divider(),
                            BKitB.make_context_section([
                                BKitB.markdown_section(f'```{traceback.format_exc()}```')
                            ])
                        ]
                        self.send_message(msg_packet['channel'], message='', blocks=blocks)
                    else:
                        self._log.error(f'Exception occurred: {exception_msg}', e)
                        self.send_message(msg_packet['channel'], f"Exception occurred: \n```{exception_msg}```")

    def handle_command(self, event_dict: dict):
        """Handles a bot command if it's known"""
        response = None
        message = event_dict['message']
        channel = event_dict['channel']
        self._log.debug(f'Incoming message: {message}')

        is_matched = False
        for resp_dict in self.commands:
            regex = resp_dict.get('pattern')
            match = re.match(regex, message)
            if match is not None:
                self._log.debug(f'Matched on pattern: {regex}')
                # We've matched on a command
                resp = resp_dict['response']
                # Add the regex pattern into the event dict
                event_dict['match_pattern'] = regex
                if isinstance(resp, list):
                    if len(resp) == 0:
                        # Empty response placeholder... Maybe we'll use this for certain commands.
                        self._log.debug('Empty list response')
                        response = None
                    elif isinstance(resp[0], dict):
                        # Response is a JSON blob for handling in Block Kit.
                        self._log.debug('JSON response')
                        response = resp
                    else:
                        # Copy the list to ensure changes aren't propagated to the command list
                        self._log.debug('Possibly command response. '
                                        'Replacing list items with variables where applicable...')
                        resp_list = resp.copy()
                        # Examine list, replace any known strings ('message', 'channel', etc.)
                        #   with event context variables
                        for k, v in event_dict.items():
                            if k in resp_list:
                                resp_list[resp_list.index(k)] = v
                        # Function with args; sometimes response can be None
                        response = self.call_command(*resp_list)
                elif callable(resp):
                    # Handle when response is just callable
                    self._log.debug('Callable response')
                    response = resp()
                else:
                    # String response
                    self._log.debug('Simple string response')
                    response = resp
                is_matched = True
                self._log.debug(f'Response is of type: {type(response)}')
                break

        if message != '' and not is_matched:
            response = f"I didn\'t understand this: *`{message}`*\n" \
                       f"Use {' or '.join([f'`{x} help`' for x in self.triggers_txt])} " \
                       f"to get a list of my commands."

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

    def parse_slash_command(self, event_data: dict):
        """Takes in info relating to a slash command that was triggered and
        determines how the command should be handled
        """
        user = event_data['user_id']
        channel = event_data['channel_id']
        command = event_data['command']
        text = event_data['text']
        un = event_data['user_name']

        processed_cmd = command.replace('/', '').replace('-', ' ')

        if text != '':
            processed_cmd += f' {text}'
        self._log.debug(f'Parsed slash command from {un}: {processed_cmd}')

        self.handle_command({'message': processed_cmd, 'channel': channel, 'user': user,
                             'raw_message': processed_cmd})

    @staticmethod
    def get_time_elapsed(st_dt: datetime) -> str:
        """Gets elapsed time between two datetimes"""
        result = relativedelta.relativedelta(datetime.now(), st_dt)

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
            attr_val = getattr(result, attr)
            if attr_val is not None:
                if attr_val > 0:
                    result_list.append('{:d}{}'.format(attr_val, attrs[attr]))
        return ' '.join(result_list)

    def convert_last_message(self, channel: str, timestamp: str, callable_list: List[Union[Callable, str]]) -> \
            Union[str, List[Dict]]:
        """Grabs the last message at a given time stamp in a given channel and applies
        a function to convert the text in the block structure"""
        last_msg = self.get_previous_msg_in_channel(channel=channel, timestamp=timestamp)
        if last_msg['text'] == "This content can't be displayed." and len(last_msg['blocks']) > 0:
            # It's a block text, so we'll need to process it
            #   Make sure a callable has been applied though
            if callable_list is None:
                return 'Callable not included in get_prev_msg... Can\'t process blocks without this!'
            return block_text_converter(blocks=last_msg['blocks'], callable_list=callable_list)
        return last_msg['text']

    def message_main_channel(self, message: str = None, blocks: Optional[List[dict]] = None):
        """Wrapper to send message to whole channel"""
        if message is not None:
            self.send_message(self.main_channel, message)
        elif blocks is not None:
            self.send_message(self.main_channel, message='', blocks=blocks)
        else:
            raise ValueError('No data passed for message.')
