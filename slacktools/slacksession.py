"""Specific routines that require more elaborate setup - e.g., sessions
    - Majority of routines from https://github.com/smashwilson/slack-emojinator/blob/master/upload.py
"""
import os
import tempfile
from urllib.parse import urlparse
import requests
from easylogger import Log


class SlackSessionNotInitException(Exception):
    pass


class ParseError(Exception):
    pass


class SlackSession:

    def __init__(self, team: str, d_cookie: str, xoxc_token: str, parent_log: Log = None):
        self.log = Log(parent_log, child_name=self.__class__.__name__)
        self.team = team
        self.d_cookie = d_cookie
        self.xoxc_token = xoxc_token
        self.log.debug(f'Cookie is {len(self.d_cookie)} chars and begins with "{self.d_cookie[:10]}".')

        base_url = f'https://{self.team}.slack.com'
        self.url_customize = f'{base_url}/customize/emoji'
        self.url_add = f'{base_url}/api/emoji.add'
        self.url_list = f'{base_url}/api/emoji.adminList'

        self.session = self.init_session()  # type: requests.Session

    def init_session(self) -> requests.Session:
        """Initializes session"""

        session = requests.session()
        session.headers = {'Cookie': self.d_cookie}
        session.url_customize = self.url_customize
        session.url_add = self.url_add
        session.url_list = self.url_list
        session.api_token = self.xoxc_token

        return session

    def refresh_xoxc_token_and_cookie(self, new_token: str, new_d_cookie: str):
        """Refreshes the cookie with a new one and re-inits the session"""
        self.xoxc_token = new_token
        self.d_cookie = new_d_cookie
        self.session = self.init_session()

    def upload_emoji(self, filepath: str) -> bool:
        """Uploads an emoji to the workspace
        NOTE: The name of the emoji is taken from the filepath
        """
        if self.session is None:
            raise SlackSessionNotInitException('Cannot initialize session. '
                                               'Session not established due to lack of cookie.')
        filename = os.path.split(filepath)[1]
        emoji_name = os.path.splitext(filename)[0]
        data = {
            'mode': 'data',
            'name': emoji_name,
            'token': self.xoxc_token
        }
        files = {'image': open(filepath, 'rb')}
        resp = self.session.post(self.session.url_add, data=data, files=files, allow_redirects=False)
        resp.raise_for_status()

        # Slack returns 200 OK even if upload fails, so check for status.
        response_json = resp.json()
        if not response_json['ok']:
            self.log.error(f"Error with uploading {emoji_name}: {response_json}")
        else:
            self.log.debug('Upload process seems successful')
        return response_json['ok']

    def _download_emoji_from_url(self, url: str, name: str = None) -> str:
        """Downloads a given emoji from a url into the temp folder, returning its path for later use"""
        # Extract the file name and type from url
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        filetype = os.path.splitext(filename)[1]
        self.log.debug(f'File name and type parsed from URL: {filename} {filetype}')
        # Set download path
        temp_dir = tempfile.gettempdir()
        fname = filename if name is None else f'{name}{filetype}'
        self.log.debug(f'Naming emoji: {fname}')
        fpath = os.path.join(temp_dir, fname)

        # Download image
        if url.startswith('data'):
            # Encoded
            data = url
        else:
            # True URL
            self.log.debug('Beginning image download...')
            resp = requests.get(url)
            data = resp.content

        # Save image to file
        write = 'wb' if isinstance(data, bytes) else 'w'
        with open(fpath, write) as f:
            self.log.debug('Writing image to file...')
            f.write(data)

        return fpath

    def upload_emoji_from_url(self, url: str, name: str = None) -> bool:
        """Uploads an emoji from a given URL with the option of changing its name"""
        # Handle downloading of emoji
        self.log.debug('Beginning emoji download process...')
        emoji_path = self._download_emoji_from_url(url=url, name=name)
        # Upload the emoji
        self.log.debug('Beginning emoji upload process...')
        result = self.upload_emoji(filepath=emoji_path)
        return result
