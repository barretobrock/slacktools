#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Slacktools.
"""
import os
import versioneer
from setuptools import setup, find_packages


here_dir = os.path.abspath(os.path.dirname(__file__))
init_fp = os.path.join(here_dir, *['slacktools', '__init__.py'])

setup_args = {
    'name': 'slacktools',
    'version': versioneer.get_version(),
    'cmdclass': versioneer.get_cmdclass(),
    'license': 'MIT',
    'description': 'A common library for working with Slack',
    'url': 'https://github.com/barretobrock/slacktools',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages(exclude=['tests']),
    'dependency_links': [
        'https://github.com/barretobrock/kavalkilu/tarball/master#egg=kavalkilu'
    ],
    'install_requires': [
        'slackclient==1.3.1',
        'tabulate==0.8.3',
        'kavalkilu @ https://github.com/barretobrock/kavalkilu/tarball/master#egg=kavalkilu'
        # 'kavalkilu @ https://github.com/barretobrock/kavalkilu/archive/master.zip#egg=kavalkilu'
    ],
}

setup(**setup_args)
