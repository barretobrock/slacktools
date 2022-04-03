#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import traceback
from datetime import datetime
from typing import (
    List,
    Union,
    Tuple,
    Optional,
    Callable
)
from easylogger import Log
from kavalkilu import DateTools
from slacktools.tools import (
    BlockKitBuilder,
    SlackTools,
    SecretStore
)


class SlackBotBase(SlackTools):
    """The base class for an interactive bot in Slack"""
    def __init__(self, slack_cred_name: str, triggers: List[str], credstore: SecretStore,
                 test_channel: str, commands: dict, cmd_categories: List[str],
                 debug: bool = False, parent_log: Log = None, use_session: bool = False):
        """
        Args:
            triggers: list of str, any specific text trigger to kick off the bot's processing of commands
                default: None. (i.e., will only trigger on @mentions)
            credstore: SimpleNamespace, contains tokens & other secrets for connecting & interacting with Slack
                required keys:
                    team: str, the Slack workspace name
                    xoxp-token: str, the user token
                    xoxb-token: str, the bot token
                optional keys:
                    cookie: str, cookie used for special processes outside
                        the realm of common API calls e.g., emoji uploads
            test_channel: str, the channel to send messages by default
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
            debug: bool, if True, will provide additional info into exceptions
        """
        self._log = Log(parent_log, child_name=self.__class__.__name__)
        super().__init__(credstore=credstore, slack_cred_name=slack_cred_name, parent_log=self._log,
                         use_session=use_session)
        self.debug = debug
        self.dt = DateTools()
        # Enforce lowercase triggers (regex will be indifferent to case anyway
        if triggers is not None:
            triggers = list(map(str.lower, triggers))

        # Set triggers to @bot and any custom text
        trigger_formatted = '|{}'.format('|'.join(triggers)) if triggers is not None else ''
        self.MENTION_REGEX = r'^(<@(|[WU].+?)>{})([.\s\S ]*)'.format(trigger_formatted)
        self.test_channel = test_channel

        self.bkb = BlockKitBuilder()
        self.commands = commands
        self.cmd_categories = cmd_categories

        auth_test = self.bot.auth_test()
        self.bot_id = auth_test['bot_id']
        self.user_id = auth_test['user_id']
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
        self._log.debug(f'Building help block')
        blocks = [
            self.bkb.make_block_section(intro, accessory=self.bkb.make_image_element(avi_url, avi_alt)),
            self.bkb.make_block_divider()
        ]
        help_dict = {cat: [] for cat in self.cmd_categories}

        for k, v in self.commands.items():
            if 'pattern' not in v.keys():
                v['pattern'] = k
            if v.get('flags') is not None:
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
                            self.bkb.make_context_section([
                                self.bkb.markdown_section(f"Exception occurred: \n*`{exception_msg}`*")
                            ]),
                            self.bkb.make_block_divider(),
                            self.bkb.make_context_section([
                                self.bkb.markdown_section(f'```{traceback.format_exc()}```')
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
        for regex, resp_dict in self.commands.items():
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

    def get_time_elapsed(self, st_dt: datetime) -> str:
        """Gets elapsed time between two datetimes"""
        return self.dt.get_human_readable_date_diff(st_dt, datetime.now())

    def get_prev_msg_in_channel(self, channel: str, timestamp: str,
                                callable_list=None) -> Optional[Union[str, List[dict]]]:
        """Gets the previous message from the channel"""
        self._log.debug(f'Getting previous message in channel {channel}')
        resp = self.bot.conversations_history(
            channel=channel,
            latest=timestamp,
            limit=10)
        if not resp['ok']:
            return None
        if 'messages' in resp.data.keys():
            msgs = resp['messages']
            last_msg = msgs[0]
            if last_msg['text'] == "This content can't be displayed." and len(last_msg['blocks']) > 0:
                # It's a block text, so we'll need to process it
                #   Make sure a callable has been applied though
                if callable_list is None:
                    return 'Callable not included in get_prev_msg... Can\'t process blocks without this!'
                return self.apply_function_to_text_from_blocks(last_msg['blocks'],
                                                               callable_list=callable_list)
            return last_msg['text']
        return None

    def apply_function_to_text_from_blocks(self, blocks: List[dict], callable_list: list) -> List[dict]:
        """
        1) Iterates through a block, grabs text, replaces it with 'placeholder_x'
        2) Take the dictionary of text with placeholders, applies a function to it,
            which replaces the text in that dictionary
        3) Takes the dictionary with the replaced text and applies it back into the block
        """
        translations_dict = {}
        for block in blocks:
            txt_dict, block_dict, n = self.nested_dict_replacer(block)
            if len(txt_dict) > 0:
                for k, v in txt_dict.items():
                    if 'text' in callable_list:
                        # Duplicate the list to avoid the original being overwritten
                        clist = callable_list.copy()
                        # Swap this string out for the actual text
                        txt_pos = clist.index('text')
                        clist[txt_pos] = v
                        translations_dict[k] = clist[0](*clist[1:])
                    else:
                        translations_dict[k] = callable_list[0](*callable_list[1:])

        # Replace blocks with translations
        for i, block in enumerate(blocks):
            txt_dict, block_dict, n = self.nested_dict_replacer(block, placeholders=translations_dict,
                                                                extract=False)
            blocks[i] = block_dict

        return blocks

    def nested_dict_replacer(self, d: dict, num: int = 0, placeholders: dict = None,
                             extract: bool = True) -> Tuple[dict, dict, int]:
        """Iterates through a nested dict, replaces items in 'text' field with placeholders and vice versa
        Args:
            d: dict, the (likely nested) input dictionary to work on
            num: int, the nth placeholder we're working on
            placeholders: dict,
                key = placeholder text,
                value = original text if extract == True otherwise translated
            extract: bool, if True, will extract from d -> placeholders
                if False, will replace placeholder text in d with translated text in placeholders
        """
        if placeholders is None:
            placeholders = {}

        for k, v in d.copy().items():
            if isinstance(v, dict):
                placeholders, d[k], num = self.nested_dict_replacer(v, num, placeholders, extract=extract)
            elif isinstance(v, list):
                for j, item in enumerate(v):
                    placeholders, d[k][j], num = self.nested_dict_replacer(item, num, placeholders,
                                                                           extract=extract)
            else:
                if k == 'text':
                    if extract:
                        placeholder = f'placeholder_{num}'
                        # Take the text and move it to the temp dict
                        placeholders[placeholder] = v
                        # Replace the value in the real dict with the placeholder
                        d[k] = placeholder
                        num += 1
                    else:
                        # Replace placeholder text with translated text
                        placeholder = d[k]
                        d[k] = placeholders[placeholder]
        return placeholders, d, num

    def message_test_channel(self, message: str = None, blocks: Optional[List[dict]] = None):
        """Wrapper to send message to whole channel"""
        if message is not None:
            self.send_message(self.test_channel, message)
        elif blocks is not None:
            self.send_message(self.test_channel, message='', blocks=blocks)
        else:
            raise ValueError('No data passed for message.')
