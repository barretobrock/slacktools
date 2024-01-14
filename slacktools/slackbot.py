#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from random import choice
import re
import traceback
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from dateutil import relativedelta
from loguru import logger
import numpy as np

from slacktools.api.actions import (
    Action,
    ActionForm,
    BlockAction,
)
from slacktools.api.events.message import Message
from slacktools.api.slash.slash import SlashCommandEvent
from slacktools.block_kit.base import (
    BlocksType,
    dictify_blocks,
)
from slacktools.block_kit.blocks import (
    ActionsBlock,
    DividerBlock,
    MarkdownContextBlock,
    MarkdownSectionBlock,
)
from slacktools.block_kit.elements.input import ButtonElement
from slacktools.command_processing import CommandItem
from slacktools.slack_input_parser import (
    SlackInputParser,
    block_text_converter,
)
from slacktools.tools import SlackTools


class SlackBotBase(SlackTools):
    """The base class for an interactive bot in Slack"""
    def __init__(self, props: Dict, triggers: List[str], main_channel: str, admins: List[str],
                 is_post_exceptions: bool = False, is_debug: bool = False, is_use_session: bool = False,
                 is_rand_response: bool = False):
        """
        Args:

            props: dict, contains tokens & other secrets for connecting &
                    interacting with Slack
                required keys:
                    team: str, the Slack workspace name
                    xoxp-token: str, the user token
                    xoxb-token: str, the bot token
                optional keys:
                    d-cookie: str, cookie used for special processes outside
                        the realm of common API calls e.g., emoji uploads
                    xoxc-token: str, token for uploading emojis
            triggers: list of str, any specific text trigger to kick off the bot's processing of commands
                default: None. (i.e., will only trigger on @mentions)
            main_channel: str, the channel to send messages by default
            admins: List[str], list of admin UIDs to allow access to admin-level commands
            is_post_exceptions: bool, if True, will post exception detail in messages
            is_debug: bool, if True, will provide additional info into exceptions
            is_use_session: bool, if True, will set up a session, namely for doing things like uploading emojis
            is_rand_response: bool, if True, will do a random response when a command is not matched
        """
        super().__init__(props=props, main_channel=main_channel, is_use_session=is_use_session)
        self.is_post_exceptions = is_post_exceptions
        self.is_debug = is_debug
        self.is_rand_response = is_rand_response
        self.rand_response_methods = []
        # Enforce lowercase triggers (regex will be indifferent to case anyway
        if triggers is not None:
            triggers = list(map(str.lower, triggers))

        # Set triggers to @bot and any custom text
        trigger_formatted = '|{}'.format('|'.join(triggers)) if triggers is not None else ''
        self.MENTION_REGEX = r'^(<@({})>{})([.\s\S ]*)'.format(self.user_id, trigger_formatted)
        self.main_channel = main_channel
        self.admins = admins

        self.commands = []  # type: List[CommandItem]

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
        self.forms = {}  # type: Dict[str, ActionForm]

    def update_commands(self, commands: List[CommandItem]):
        """Updates the dictionary of commands"""
        self.commands = commands

    @staticmethod
    def build_command_blocks(command_item: CommandItem) -> BlocksType:
        tab_char = ':blank:'  # this is wonky, but it works much better than \t in Slack!

        content_block_items = [
            f'Matches on: *`{command_item.pattern}`*',
        ]

        flags_txt = ''
        examples_txt = ''
        if len(command_item.flags) > 0:
            flags_desc = f'\n{tab_char}'.join([f' -> *`{x}`*' for x in command_item.flags])
            flags_txt += f'\n{tab_char}Optional Flags:\n{tab_char}{flags_desc}'
            content_block_items.append(flags_txt)
        if len(command_item.examples) > 0:
            examples_desc = f'\n{tab_char}'.join([f' -> *`{x}`*' for x in command_item.examples])
            examples_txt += f'\n{tab_char}Examples:\n{tab_char}{examples_desc}'
            content_block_items.append(examples_txt)

        return [
            MarkdownSectionBlock([
                f'*{command_item.title}*',
                f'_{command_item.desc}_'
            ]),
            MarkdownContextBlock(content_block_items),
            DividerBlock()
        ]

    @dictify_blocks
    def build_help_block(self, intro: str, avi_url: str, avi_alt: str) -> BlocksType:
        """Builds bot's description of functions into a giant wall of help text
        Args:
            intro: str, The bot's introduction
            avi_url: str, the url to the image to display next to the intro
            avi_alt: str, alt text for the avatar

        Returns:
            list of dict, Block Kit-ready help text
        """
        logger.debug('Building help block')
        # Build out some explanation of the main commands
        main_cmd_blocks = []
        for cmd_item in self.commands:
            if 'main' not in cmd_item.tags:
                continue
            main_cmd_blocks += self.build_command_blocks(cmd_item)

        # Then build out a list of the groups
        groups = [c.group for c in self.commands]
        unique_groups = sorted(list(set(groups)))
        group_btns = [
            ButtonElement(f'{x} {self.tiny_text_gen(f"{groups.count(x)}")}', action_id=f'shelpg-{x}')
            for x in unique_groups
        ]
        # Then build out a list of the tags
        tags = []
        for cmd in self.commands:
            if cmd.tags is not None:
                tags += cmd.tags
        unique_tags = sorted(list(set(tags)))
        tag_btns = [
            ButtonElement(f'{x} {self.tiny_text_gen(f"{tags.count(x)}")}', action_id=f'shelpt-{x}')
            for x in unique_tags
        ]

        blocks = [
            MarkdownSectionBlock(intro, image_url=avi_url, image_alt_txt=avi_alt),
            DividerBlock()
            ] + main_cmd_blocks + [
            MarkdownContextBlock(f'*Command groups {self.tiny_text_gen("(total commands)")}:*'),
            ActionsBlock(group_btns),
            MarkdownContextBlock(f'*Command tags {self.tiny_text_gen("(total commands)")}:*'),
            ActionsBlock(tag_btns),
            MarkdownContextBlock('Additionally, just tell Wizzy `shelp -t {tag}` or `shelp -g {group}` any time!'),
        ]

        return blocks

    @dictify_blocks
    def search_help_block(self, message: str) -> Union[BlocksType, str]:
        """Takes in a message and filters command descriptions for output"""
        logger.debug(f'Got help search command: {message}')
        group = SlackInputParser.get_flag_from_command(message, flags=['g'], default=None)
        tag = SlackInputParser.get_flag_from_command(message, flags=['t'], default=None)

        if group is not None:
            logger.debug(f'Filtering on group: {group}')
            filtered_by = f'group: {group}'
            cmd_list = [x for x in self.commands if x.group == group]
        elif tag is not None:
            logger.debug(f'Filtering on tag: {tag}')
            filtered_by = f'tag: {tag}'
            cmd_list = [x for x in self.commands if tag in x.tags]
        else:
            logger.debug('Unable to filter on group or tag. Responding to user.')
            return 'Unable to filter on commands without a tag or group. Please either include ' \
                   '`-t <tag-name>` or `-g <group-name>`'

        logger.debug(f'Found {len(cmd_list)} cmds matching {filtered_by}')
        result_blocks = []
        for cmd_item in cmd_list:
            result_blocks += self.build_command_blocks(cmd_item)

        return [
            MarkdownContextBlock(f'*`{len(cmd_list)}/{len(self.commands)}`* commands filtered by {filtered_by}')
        ] + result_blocks + [
            ActionsBlock([
                ButtonElement('Back to Menu', action_id='help', style='primary'),
                ButtonElement('Close', action_id='close', style='danger')
            ])
        ]

    def parse_direct_mention(self, message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parses user and other text from direct mention"""
        matches = re.search(self.MENTION_REGEX, message, re.IGNORECASE)
        if matches is not None:
            if matches.group(1).lower() in self.triggers:
                # Matched using abbreviated triggers
                trigger = matches.group(1).lower()
                logger.debug(f'Matched on abbreviated trigger: {trigger}, msg: {message}')
            else:
                # Matched using bot id
                trigger = matches.group(2)
                logger.debug(f'Matched on bot id: {trigger}, msg: {message}')
            message_txt = matches.group(3).lower().strip()
            raw_message = matches.group(3).strip()
            return trigger, message_txt, raw_message
        return None, None, None

    def parse_message_event(self, resp_dict: Dict, users_dict: Dict = None):
        """Takes in an Events API message-triggered event dict and determines
         if a command was issued to the bot"""
        event_dict = resp_dict['event']
        event_type = event_dict['type']
        if event_type != 'message':
            return
        message_obj = Message(event_dict)
        # event_data = MessageEvent(event_dict=event_dict)

        # Determine whether to process this message as a command
        is_handle = False
        if message_obj.subtype is None or message_obj.subtype == 'message_replied':
            trigger, message, raw_message = self.parse_direct_mention(message_obj.raw_text)
            if trigger in self.triggers:
                if message_obj.message_hash not in self.message_events:
                    is_handle = True
                    self.message_events.append(message_obj.message_hash)
                    message_obj.take_processed_message(clean_msg=message, raw_message=raw_message)

        if is_handle:
            try:
                self.handle_command(message_obj, users_dict=users_dict)
            except Exception as e:
                exception_msg = '{}: {}'.format(e.__class__.__name__, e)
                logger.error(f'Exception occurred: {exception_msg}', e)
                if not isinstance(e, RuntimeError) and self.is_post_exceptions:
                    if self.is_debug:
                        blocks = [
                            MarkdownContextBlock(f"Exception occurred: \n*`{exception_msg}`*").asdict(),
                            DividerBlock().asdict(),
                            MarkdownContextBlock(f'```{traceback.format_exc()}```').asdict()
                        ]
                        self.send_message(message_obj.channel_id, message='', blocks=blocks,
                                          thread_ts=message_obj.thread_ts)
                    else:
                        self.send_message(message_obj.channel_id, f"Exception occurred: \n```{exception_msg}```",
                                          thread_ts=message_obj.thread_ts)

    def parse_action_form(self, block_action: BlockAction) -> Tuple[bool, Optional[Union[ActionForm, Action]]]:
        """Handles organizing an incoming event into a structure that's easier to wield across the bots/forms"""

        action_id = block_action.get_action_id()
        logger.debug(f'Receiving action: {action_id} from user {block_action.user.id}')

        # Determine if it's a part of a form
        matched_form_key = next((f_key for f_key, form in self.forms.items() if action_id.startswith(f_key)), None)
        if matched_form_key is not None:
            # Matched to form. Process the action and check for is_complete.
            self.forms[matched_form_key].add_resp_item(resp_item=block_action.action)
            if not self.forms[matched_form_key].is_complete:
                # Pop form out of dict
                return False, None
            form = self.forms.pop(matched_form_key)
            return True, form
        else:
            # Action form is not registered
            logger.warning(f'Unregistered action form: {action_id}. Cannot proceed')
            return False, None

    @staticmethod
    def check_user_for_bot_timeout(users_dict: Dict, uid: str) -> bool:
        logger.debug('Begin permissions check...')
        user_obj = users_dict.get(uid)
        if user_obj is None:
            logger.info('User not in system. Bypassing check.')
        elif user_obj.is_in_bot_timeout:
            logger.info(f'User with name {user_obj.display_name} is in bot timeout. Ignoring all requests.')
            return True
        return False

    def handle_command(self, obj: Union[Message, SlashCommandEvent], users_dict: Dict = None):
        """Handles a bot command if it's known"""
        response = None
        is_slash = isinstance(obj, SlashCommandEvent)
        logger.debug(f'Incoming message: {obj.cleaned_message}')
        uid = obj.user_id if is_slash else obj.user

        if users_dict is not None:
            if self.check_user_for_bot_timeout(users_dict=users_dict, uid=uid):
                return None

        is_matched = False
        for cmd_item in self.commands:
            match = re.match(cmd_item.pattern, obj.cleaned_message)
            if match is not None:
                logger.debug(f'Matched on pattern: {cmd_item.pattern}')
                group = cmd_item.group
                if group == 'admin':
                    if uid not in self.admins:
                        logger.info(f'Blocked user {uid} from using command.')
                        response = ':ah-ah-ah:' * np.random.randint(1, 50)
                        break
                # We've matched on a command
                resp = cmd_item.response
                # Add the regex pattern into the event dict
                obj.take_match_pattern(cmd_item.pattern)
                if isinstance(resp, list):
                    if len(resp) == 0:
                        # Empty response placeholder... Maybe we'll use this for certain commands.
                        logger.warning('Empty list response')
                        response = None
                    elif isinstance(resp[0], dict):
                        # Response is a JSON blob for handling in Block Kit.
                        logger.debug('JSON response')
                        response = resp
                    else:
                        # Copy the list to ensure changes aren't propagated to the command list
                        logger.debug('Possibly command response. '
                                     'Replacing list items with variables where applicable...')
                        resp_list = resp.copy()
                        # Examine list, replace any known strings ('message', 'channel', etc.)
                        #   with event context variables
                        for k, v in obj.__dict__.items():
                            if k in resp_list:
                                resp_list[resp_list.index(k)] = v
                        # Function with args; sometimes response can be None
                        response = self.call_command(*resp_list)
                elif callable(resp):
                    # Handle when response is just callable
                    logger.debug('Callable response')
                    response = resp()
                else:
                    # String response
                    logger.debug('Simple string response')
                    response = resp
                is_matched = True
                logger.debug(f'Response is of type: {type(response)}')
                break

        if obj.cleaned_message != '' and not is_matched:
            if self.is_rand_response and len(self.rand_response_methods) > 0:
                method = choice(self.rand_response_methods)
                if isinstance(method, list):
                    callable_method = method.pop(0)
                    # Append the original message
                    method_args = method
                    method_args.append(obj.cleaned_message)
                else:
                    # Only method supplied
                    callable_method = method
                    method_args = [obj.cleaned_message]
                response = callable_method(*method_args)
            else:
                response = f"I didn\'t understand this: *`{obj.cleaned_message}`*\n" \
                           f"Use {' or '.join([f'`{x} help`' for x in self.triggers_txt])} " \
                           f"to get a list of my commands."
        if response is None:
            return

        params = {
            'channel': obj.channel_id,
            'thread_ts': obj.thread_ts
        }
        if isinstance(response, str):
            try:
                response = response.format(**obj.__dict__)
            except KeyError:
                # Response likely has some curly braces in it that disrupt str.format().
                # Pass string without formatting
                pass
            params.update({'message': response})
        elif isinstance(response, list):
            # Likely blocks response
            params.update({'message': '', 'blocks': response})
        self.send_message(**params)

    @staticmethod
    def call_command(cmd: Callable, *args, **kwargs):
        """
        Calls the command referenced while passing in arguments
        :return: None or string
        """
        return cmd(*args, **kwargs)

    def parse_slash_command(self, event_dict: Dict, users_dict: Dict = None):
        """Takes in info relating to a slash command that was triggered and
        determines how the command should be handled
        """
        event_data = SlashCommandEvent(event_dict=event_dict)
        logger.debug(f'Parsed slash command from {event_data.user_name}: {event_data.cleaned_command}')

        self.handle_command(event_data, users_dict=users_dict)

    @staticmethod
    def _relativedelta_to_human(reldelta: relativedelta.relativedelta) -> str:
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
            attr_val = getattr(reldelta, attr)
            if attr_val is not None:
                if attr_val > 0:
                    result_list.append('{:d}{}'.format(attr_val, attrs[attr]))
        return ' '.join(result_list)

    @classmethod
    def timedelta_to_human(cls, tdelta: timedelta) -> str:
        """Converts timedelta to a human-readable string"""
        # Convert to relativedelta
        rdelta = relativedelta.relativedelta(seconds=int(tdelta.total_seconds()), microseconds=tdelta.microseconds)
        return cls._relativedelta_to_human(reldelta=rdelta)

    @classmethod
    def get_time_elapsed(cls, st_dt: datetime, end_dt: datetime = None) -> str:
        """Gets elapsed time between two datetimes"""
        if end_dt is None:
            end_dt = datetime.now()
        result = relativedelta.relativedelta(end_dt, st_dt)

        return cls._relativedelta_to_human(result)

    def convert_last_message(self, channel: str, timestamp: str, callable_list: List[Union[Callable, str]]) -> \
            Union[str, List[Dict]]:
        """Grabs the last message at a given time stamp in a given channel and applies
        a function to convert the text in the block structure"""
        last_msg: Message
        last_msg = self.get_previous_msg_in_channel(channel=channel, timestamp=timestamp)
        if last_msg.text == "This content can't be displayed." and len(last_msg.blocks) > 0:
            # It's a block text, so we'll need to process it
            #   Make sure a callable has been applied though
            if callable_list is None:
                return 'Callable not included in get_prev_msg... Can\'t process blocks without this!'
            return block_text_converter(blocks=last_msg.blocks, callable_list=callable_list)
        return last_msg.text

    def message_main_channel(self, message: str = None, blocks: BlocksType = None,
                             thread_ts: str = None):
        """Wrapper to send message to whole channel"""
        if message is not None:
            self.send_message(self.main_channel, message, thread_ts=thread_ts)
        elif blocks is not None:
            self.send_message(self.main_channel, message='', blocks=blocks, thread_ts=thread_ts)
        else:
            raise ValueError('No data passed for message.')

    def private_message_main_channel(self, user_id: str, message: str = None, blocks: BlocksType = None,
                                     thread_ts: str = None):
        """Wrapper to send message to whole channel"""
        if message is None:
            message = 'An important message from the Federation.'

        self.private_channel_message(user_id=user_id, channel=self.main_channel, message=message, blocks=blocks,
                                     thread_ts=thread_ts)
