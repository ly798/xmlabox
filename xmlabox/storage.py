import os
import json
import logging

from xmlabox.base import Track

LOG = logging.getLogger(__name__)
content = {'cookie': None, 'current_play': None, 'volume': 0}
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
            self._cookie = stor.get('cookie')
            self._current_paly = stor.get('current_play')
            self._volume = stor.get('volume')

    def save(self):
        with open(self.file_path, 'w') as f:
            f.write(
                json.dumps({
                    'cookie': self._cookie,
                    'current_play': self._current_paly,
                    'volume': self._volume
                }))

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, cookie):
        self._cookie = cookie

    @property
    def current_play(self):
        if self._current_paly:
            return Track(**self._current_paly)
        return {}

    @current_play.setter
    def current_paly(self, current_paly):
        self._current_paly = current_paly.json()

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume):
        self._volume = volume