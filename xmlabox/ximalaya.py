import requests
import time
import hashlib
import random
import logging

from pprint import pprint

from xmlabox.base import Album, Track, User

LOG = logging.getLogger(__name__)


class ximalaya(object):
    def __init__(self, cookie):
        _headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
            "Cookie": cookie
        }
        self.session = requests.session()
        self.session.headers.update(_headers)

    def getServerTime(self):
        """
        获取喜马拉雅服务器的时间戳
        :return:
        """
        serverTimeUrl = "https://www.ximalaya.com/revision/time"
        response = self.session.get(serverTimeUrl)
        return response.text

    def getSign(self, serverTime):
        """
        生成 xm-sign
        规则是 md5(ximalaya-服务器时间戳)(100以内随机数)服务器时间戳(100以内随机数)现在时间戳
        :param serverTime:
        :return:
        """
        nowTime = str(round(time.time() * 1000))
        sign = str(
            hashlib.md5("himalaya-{}".format(serverTime).encode()).hexdigest()
        ) + "({})".format(str(round(
            random.random() * 100))) + serverTime + "({})".format(
                str(round(random.random() * 100))) + nowTime
        return sign

    def sign(self):
        serverTime = self.getServerTime()
        sigin = self.getSign(serverTime)
        self.session.headers.update({"xm-sign": sigin})
        print(sigin)

    def get_current_user(self):
        # 当前用户
        url = 'https://www.ximalaya.com/revision/main/getCurrentUser'
        info = self.session.get(url).json()
        data = info.get('data')
        user = User(username=data.get('nickname', None))
        return user

    def get_current_user_info(self):
        # 用户详细信息
        url = 'https://www.ximalaya.com/revision/my/getCurrentUserInfo'
        info = self.session.get(url).json()
        return info

    def get_subscribe(self):
        # 订阅
        #TODO: 分页
        url = "https://www.ximalaya.com/revision/album/v1/sub/comprehensive?num=1&size=30&subType=2&category=all"
        info = self.session.get(url).json()
        data = info.get('data')
        result = []
        for i in data.get('albumsInfo'):
            result.append(
                Album(name=i.get('title'),
                      id=i.get('id'),
                      author=i.get('anchor').get('anchorNickName'),
                      track_count=i.get('trackCount'),
                      description=i.get('description')))

        return result

    def get_history(self, page_num=1, page_size=10):
        # 历史
        url = "https://www.ximalaya.com/revision/my/getListened"
        info = self.session.get(url).json()
        data = info.get('data')
        total_count = data.get('totalCount')
        pages = total_count // page_size if total_count % page_size == 0 else total_count // page_size + 1
        result = []

        def _tmp(lst):
            for i in lst:
                track = Track(name=i.get('trackTitle'),
                              id=i.get('trackId'),
                              album_name=i.get('albumName'),
                              album_id=i.get('albumId'),
                              duration=i.get('trackDuration'))
                result.append(track)

        _tmp(data.get('today'))
        _tmp(data.get('yesterday'))
        _tmp(data.get('earlier'))
        return {
            'data': result[(page_num - 1) * page_size:page_num * page_size],
            'total_count': total_count,
            'page_num': page_num,
            'page_size': page_size,
            'pages': pages
        }

    def get_track_src(self, id, type=1):
        """获取播放src"""
        url = "https://www.ximalaya.com/revision/play/v1/audio?id=%s&ptype=%s" % (
            id, type)
        info = self.session.get(url).json()
        return info.get('data').get('src')

    def get_album_info(self, id):
        url = "https://www.ximalaya.com/revision/album?albumId=%s" % id
        info = self.session.get(url).json().get('data')
        return Album(name=info.get('mainInfo').get('albumTitle'),
                     id=id,
                     author=info.get('anchorInfo').get('anchorName'),
                     description=info.get('mainInfo').get('shortIntro'),
                     track_count=info.get('tracksInfo').get('trackTotalCount'))

    def get_track_list(self, id, page_num=1, page_size=10):
        #获取专辑的所有章节
        url = "https://www.ximalaya.com/revision/album/v1/getTracksList?albumId=%s&pageNum=%s&pageSize=%s" % (
            id, page_num, page_size)
        info = self.session.get(url).json().get('data')
        total_count = info.get('trackTotalCount')
        pages = total_count // page_size if total_count % page_size == 0 else total_count // page_size + 1
        result = []
        album_name = self.get_album_info(id).name
        for i in info.get('tracks'):
            track = Track(name=i.get('title'),
                          id=i.get('trackId'),
                          album_name=album_name,
                          album_id=id,
                          duration=i.get('duration'),
                          is_history=False)
            result.append(track)

        return {
            'data': result,
            'total_count': total_count,
            'page_num': page_num,
            'page_size': page_size,
            'pages': pages
        }

    def get_next_track(self, id):
        url = "https://www.ximalaya.com/revision/play/v1/show?id=%s&sort=0&size=10&ptype=1" % id
        info = self.session.get(url).json()
        index = -1
        album_id = -1
        for i in info.get('data').get('tracksAudioPlay'):
            if str(i.get('trackId')) == str(id):
                index = i.get('index')
                album_id = i.get('albumId')
        LOG.debug('get next index: %s' % str(index + 1))
        _tmp = self.get_track_list(album_id, index + 1, 1)
        track = _tmp.get('data')[0]
        return track

    def get_track_token(self, id):
        url = "https://www.ximalaya.com/nyx/v2/track/count/web"
        _headers = {
            "Host": "www.ximalaya.com",
            "Origin": "https://www.ximalaya.com",
            "Referer": "https://www.ximalaya.com/"
        }
        self.session.headers.update(_headers)
        info = self.session.post(url, data={'trackId': str(id)}).json()
        return info.get('data').get('token')

    def commit_process(self, id, sec):
        url = "https://www.ximalaya.com/nyx/v2/track/statistic/web"
        token = self.get_track_token(id)
        now = round(time.time() * 1000)
        data = {
            "trackId": id,
            # "albumId": "18515643",
            "startedAt": now - sec * 1000,
            "endedAt": now,
            "duration": "1",
            # "breakSecond": "0",
            "token": token
        }
        _headers = {
            "Host": "www.ximalaya.com",
            "Origin": "https://www.ximalaya.com",
            "Referer": "https://www.ximalaya.com/"
        }
        info = self.session.post(url, data=data).json()
        return info


if __name__ == "__main__":
    cookie = ""
    s = ximalaya(cookie)
    # pprint(s.get_next_track('143744918').json())
    pprint(s.get_next_track('143744919').json())
    # pprint(s.get_track_list('18515643').json())
    # pprint(s.get_history().json())
    # pprint(s.get_track_src('132052945').json())