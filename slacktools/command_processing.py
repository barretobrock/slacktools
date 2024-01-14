#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    TypedDict,
    Union,
)

from loguru import logger
import yaml

LOG = logger


class CommandItem:
    pattern: str
    title: str
    tags: List[str]
    group: str
    desc: str
    flags: List[str]
    examples: List[str]
    response: Union[str, List[Union[Callable, str]], List[str]] = 'i\'m empty!'
    is_text_response: bool = True

    def __init__(self, group: str, pattern: str, cmd_details: Dict, obj):
        self.group = group
        self.pattern = pattern
        self.title = cmd_details.get('title', pattern)
        self.desc = cmd_details.get('desc', '')
        self.tags = cmd_details.get('tags', [])

        if 'response_cmd' in cmd_details.keys():
            resp_item = CommandResponseItem(**cmd_details.get('response_cmd', {}))
            self.flags = cmd_details.get('flags', [])
            self.examples = cmd_details.get('examples', [])
            LOG.debug(f'Searching for callable "{resp_item.callable_name}" in object {obj.__class__.__name__}...')
            callable_obj = getattr(obj, resp_item.callable_name, None)  # type: callable
            if callable_obj is not None:
                LOG.debug(f'Binding callable and {len(resp_item.args)} args to response')
                self.response = [callable_obj] + resp_item.args
                self.is_text_response = False
            else:
                raise ValueError(f'Was not able to bind a method. '
                                 f'Callable not found by name: {resp_item.callable_name} in {obj.__class__.__name__}.')
        elif 'response_txt' in cmd_details.keys():
            self.response = cmd_details.get('response_txt')

    def __getattr__(self, item):
        # This helps to avoid getting AttributeError on values.
        #   Instead they'll just return None, which is the pattern
        #   we want to work with.
        return None

    def __repr__(self):
        return f'<CommandItem(name={self.title}, is_text_response={self.is_text_response})>'


class CommandResponseItem:
    callable_name: str
    args: List[str]

    def __init__(self, callable_name: str, args: List[str] = None, **kwargs):
        self.callable_name = callable_name
        self.args = args if args is not None else []
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __repr__(self):
        return f'<CommandResponseItem(name={self.callable_name}, args={len(self.args)})>'


def build_commands(bot_obj, cmd_yaml_path: Path, log: logger) -> List[CommandItem]:
    """Reads in commands from a YAML file and builds out their structure, searching for named attributes
    as callables along the way"""

    with cmd_yaml_path.open() as f:
        cmd_dict = yaml.safe_load(f)

    processed_cmds = []
    for group_name, group_dict in cmd_dict['commands'].items():
        group = group_name.replace('group-', '').replace('-', ' ').lower()
        log.debug(f'Working on group {group}...')
        for cmd_regex, cmd_details in group_dict.items():
            log.debug(f'Working on command: {cmd_regex}')
            processed_cmds.append(
                CommandItem(group=group, pattern=cmd_regex, cmd_details=cmd_details, obj=bot_obj)
            )

    return processed_cmds
