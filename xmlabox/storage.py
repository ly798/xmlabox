import os
import json
import logging

from xmlabox.base import Track

LOG = logging.getLogger(__name__)
content = {'cookie': None, 'current_play': None}
default_path = os.path.join(os.getenv('HOME'), '.xmlabox/xmla.json')


class Storage:
    def __init__(self, file_path=default_path):
        self.file_path = file_path
        self.file_dir = os.path.dirname(self.file_path)
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write(json.dumps(content))
        self._load_json()

    def _load_json(self):
        with open(self.file_path, 'r') as f:
            stor = json.load(f)
            self.cookie = stor.get('cookie')
            self.current_paly = stor.get('current_play')

    def _save_file(self):
        with open(self.file_path, 'w') as f:
            f.write(
                json.dumps({
                    'cookie': self.cookie,
                    'current_play': self.current_paly
                }))

    def set_cookie(self, cookie):
        self.cookie = cookie
        self._save_file()

    def get_cookie(self):
        self._load_json()
        return self.cookie

    def set_current_paly(self, current_paly):
        self.current_paly = current_paly.json()
        self._save_file()

    def get_current_play(self):
        self._load_json()
        if self.current_paly:
            return Track(**self.current_paly)
        return {}