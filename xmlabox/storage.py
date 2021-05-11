import os
import logging
import pickle
import re
import time

import requests

LOG = logging.getLogger(__name__)
default_path = os.path.join(os.getenv('HOME'), '.xmlabox/xmla.data')
cache_dirpath = os.path.join(os.getenv('HOME'), '.xmlabox', 'cache')
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
}

expire_time = 7 * 3600


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


def local_track_cache(url, local=True):
    if not local:
        return url
    m = re.match('^.+?/([\w-]+\.m4a).*?$', url)
    if not m:
        LOG.debug("can't match")
        return
    path = os.path.join(cache_dirpath, m.groups()[0])

    if not os.path.exists(cache_dirpath):
        os.makedirs(cache_dirpath)

    if not os.path.exists(path):
        # 下载
        LOG.debug('downlond file: %s' % url)
        res = requests.get(url, headers=headers, stream=True)
        with open(path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        LOG.debug('downlond success: %s' % path)
    else:
        LOG.debug('cache exist: %s' % path)

    # 过期时间
    now = time.time()
    for i in os.listdir(cache_dirpath):
        tmp_file = os.path.join(cache_dirpath, i)
        if not tmp_file == path:
            t = os.path.getatime(tmp_file)
            if now - t >= expire_time:
                LOG.info('delete expire file: %s' % tmp_file)
                os.remove(tmp_file)

    # TODO 判断大小

    return path
