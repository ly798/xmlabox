import os
import json
import logging

from xmlabox.base import Track

LOG = logging.getLogger(__name__)
content = {'cookie': None, 'volume': 0, 'rate': 1.0, 'local_history': []}
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
            self._volume = stor.get('volume')
            self._rate = stor.get('rate')
            self._local_history = stor.get('local_history')

    def save(self):
        with open(self.file_path, 'w') as f:
            f.write(
                json.dumps({
                    'cookie': self._cookie,
                    'volume': self._volume,
                    'rate': self._rate,
                    'local_history': self._local_history
                }))

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, cookie):
        self._cookie = cookie

    @property
    def current_play(self):
        if self._local_history:
            return Track(**self._local_history[0])
        return {}

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume):
        self._volume = volume

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    @property
    def local_history(self):
        return [Track(**i) for i in self._local_history]

    def add_current_play(self, play):
        for i in range(len(self._local_history)):
            LOG.debug(play.album_id)
            LOG.debug(self._local_history[i].get('album_id'))
            if play.album_id == self._local_history[i].get('album_id'):
                self._local_history.pop(i)
                break
        self._local_history.insert(0, play.json())