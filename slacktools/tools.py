#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import string
import pandas as pd
from types import SimpleNamespace
from typing import (
    Dict,
    List
)
from random import randint
from tabulate import tabulate
from loguru import logger
from slacktools.slack_methods import SlackMethods
from slacktools.slack_input_parser import SlackInputParser


class SlackTools(SlackInputParser, SlackMethods):
    """Tools to make working with Slack API better"""

    def __init__(self, bot_cred_entry: SimpleNamespace, parent_log: logger, use_session: bool = False):
        """
        Args:
            bot_cred_entry: SecretStore entry, contains tokens & other secrets for connecting &
                    interacting with Slack
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
        super().__init__(bot_cred_entry=bot_cred_entry, parent_log=parent_log, use_session=use_session)
        self.log = parent_log.bind(child_name=self.__class__.__name__)

    def refresh_xoxc_token(self, new_token: str):
        if self.session is not None:
            self.session.refresh_xoxc_token_and_cookie(new_token=new_token, new_d_cookie=self.d_cookie)

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

    @staticmethod
    def _build_emoji_char_dict() -> dict:
        """Sets up use of replacing words with slack emojis"""
        a2z = string.ascii_lowercase
        letter_grp = [
            'regional_indicator_',
            'letter-',
            'alphabet-yellow-',
            'alphabet-white-'
            'scrabble-'
        ]

        grp = [['{}{}'.format(y, x) for x in a2z] for y in letter_grp]
        letter_dict: Dict[str, List[str]]
        letter_dict = {}

        for i, ltr in enumerate(list(a2z)):
            ltr_list = []
            for g in grp:
                ltr_list.append(g[i])
            letter_dict[ltr] = ltr_list

        # Add in consistent numbers
        for i in range(10):
            letter_dict[f'{i}'] = [f'mana{i}']

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
            '.': ['black_circle', 'period'],
            '!': ['exclamation', 'heavy_heart_exclamation_mark_ornament', 'grey_exclamation'] +
                 [f'alphabet-{x}-exclamation' for x in ['yellow', 'white']],
            '?': ['question', 'grey_question', 'questionman', 'question_block'] +
                 [f'alphabet-{x}-question' for x in ['yellow', 'white']],
            '"': ['airquotes-start', 'airquotes-end'],
            "'": ['airquotes-start', 'airquotes-end'],
            "@": [f'alphabet-{x}-at' for x in ['yellow', 'white']],
            "#": [f'alphabet-{x}-hash' for x in ['yellow', 'white']]
        }

        for k, v in addl.items():
            if k in letter_dict.keys():
                letter_dict[k] = letter_dict[k] + v
            else:
                letter_dict[k] = v
        return letter_dict

    def build_phrase(self, phrase: str) -> str:
        """Build your awesome phrase"""

        letter_dict = self._build_emoji_char_dict()
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
