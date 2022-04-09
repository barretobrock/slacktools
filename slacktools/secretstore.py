import json
from types import SimpleNamespace
from typing import Dict
from pathlib import Path
from pykeepass import PyKeePass
from pykeepass.entry import Entry


class SecretStore:
    KEY_DIR = Path().home().joinpath('keys')
    DEFAULT_FILE_NAME = 'secretprops.kdbx'
    DEFAULT_PASSWORD_FILE = 'SECRETPROP'

    def __init__(self, fname: str = DEFAULT_FILE_NAME, password: str = None,
                 password_fname: str = DEFAULT_PASSWORD_FILE):
        self.db = None

        if password_fname is not None and password is None:
            with open(self.KEY_DIR.joinpath(password_fname)) as f:
                password = f.read().strip()
        # Read in the database
        self.load_database(fname, password)

    def load_database(self, fname: str, password: str):
        self.db = PyKeePass(self.KEY_DIR.joinpath(fname), password=password)

    def get_entry(self, entry_name: str) -> Entry:
        return self.db.find_entries(title=entry_name, first=True)

    def get_key(self, key_name: str) -> Dict:
        entry = self.get_entry(key_name)
        if entry is None:
            return {}
        if any([x is not None for x in [entry.username, entry.password]]):
            resp = {
                'un': entry.username,
                'pw': entry.password
            }
        else:
            resp = {}
        if len(entry.attachments) > 0:
            for att in entry.attachments:
                # For attachments, try to decode any that we might expect. For now, that's just JSON
                if isinstance(att.data, bytes):
                    # Decode to string, try loading as json
                    try:
                        file_contents = json.loads(att.data.decode('utf-8'))
                        resp.update(file_contents)
                    except Exception:
                        resp[att.filename] = att.data.decode('utf-8')
        resp.update(entry.custom_properties)
        return resp

    def get_key_and_make_ns(self, entry: str) -> SimpleNamespace:
        entry_dict = self.get_key(entry)
        processed_dict = {}
        for k, v in entry_dict.items():
            processed_dict[k.replace('-', '_')] = v
        return SimpleNamespace(**processed_dict)
