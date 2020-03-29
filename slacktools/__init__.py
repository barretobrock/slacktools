#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack Tools: A common library for working with Slack
"""
from .slackbot import SlackBotBase
from .tools import SlackTools, GSheetReader, BlockKitBuilder
from .events_fork import SlackEventAdapter


from ._version import get_versions
__version__ = get_versions()['version']
__update_date__ = get_versions()['date']
del get_versions
