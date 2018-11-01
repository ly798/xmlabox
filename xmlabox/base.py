class Item:
    def __init__(self, name, display_name, func):
        self.name = name
        self.display_name = display_name
        self.func = func

    @property
    def comment(self):
        return ''

    def __str__(self):
        return '<Item: %s>' % self.name


class User:
    def __init__(self, username):
        self.username = username

    def is_login(self):
        return bool(self.username)

    def __str__(self):
        return '<User: %s>' % self.username


class Album:
    def __init__(self, name, id, author, description, track_count=0):
        self.name = name
        self.id = id
        self.author = author
        self.description = description
        self.track_count = track_count

    @property
    def display_name(self):
        return '%s - %s' % (self.name, self.author)

    @property
    def comment(self):
        return ''

    def __str__(self):
        return '<Album: %s>' % self.name


class Track:
    def __init__(self,
                 name,
                 id,
                 album_name,
                 album_id,
                 duration,
                 cursor=0,
                 time=0,
                 length=0,
                 position=0,
                 src=None,
                 is_history=True):
        self.name = name
        self.id = id
        self.album_name = album_name
        self.album_id = album_id
        self.duration = duration
        self.cursor = cursor
        self.time = time
        self.length = length
        self.position = position
        self.src = src
        # 如果是history，显示的是专辑名，comment显示的是章节名
        self.is_histroy = is_history

    @property
    def display_name(self):
        if self.is_histroy:
            return self.album_name
        return self.name

    @property
    def comment(self):
        if self.is_histroy:
            return '%s - %s' % (self.name, self.duration)
        return '%s - %s' % (self.album_name, self.duration)

    # @property
    # def src(self):
    #     if not self._src:
    #         self._src = ximalaya.get_next_track(self.id)
    #     return self._src

    def json(self):
        return {
            'name': self.name,
            'id': self.id,
            'album_name': self.album_name,
            'album_id': self.album_id,
            'duration': self.duration,
            'time': self.time,
            'length': self.length,
            'position': self.position,
            'cursor': self.cursor,
            'src': self.src
        }

    def __str__(self):
        return '<Track: %s>' % self.name