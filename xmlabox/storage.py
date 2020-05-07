import os
import logging
import pickle

LOG = logging.getLogger(__name__)
default_path = os.path.join(os.getenv('HOME'), '.xmlabox/xmla.data')


class Storage:
    def __init__(self, file_path=default_path):
        # 默认值
        self._cookie = None
        self._volume = 50
        self._rate = 1.0
        self._local_history = []

        self.file_path = file_path
        self.file_dir = os.path.dirname(self.file_path)

        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)

        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, 'rb') as f:
            stor = pickle.load(f)
            self._cookie = stor._cookie
            self._volume = stor._volume
            self._rate = stor._rate
            self._local_history = stor._local_history

    def save(self):
        with open(self.file_path, 'wb') as f:
            pickle.dump(self, f)

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, cookie):
        self._cookie = cookie

    @property
    def current_play(self):
        if self._local_history:
            return self._local_history[0]
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
        return self._local_history

    def add_current_play(self, play):
        for i in range(len(self._local_history)):
            if play.album_id == self._local_history[i].album_id:
                self._local_history.pop(i)
                break
        self._local_history.insert(0, play)