import vlc


class Player:
    def __init__(self, *args):
        if args:
            instance = vlc.Instance(*args)
            self.media = instance.media_player_new()
        else:
            self.media = vlc.MediaPlayer()

    def set_uri(self, uri):
        self.media.set_mrl(uri)

    def play(self, path=None):
        if path:
            self.set_uri(path)
            return self.media.play()
        else:
            return self.media.play()

    def add_callback(self, event_type, callback, *args, **kwds):
        self.media.event_manager().event_attach(event_type, callback, *args,
                                                **kwds)

    def get_time(self):
        return self.media.get_time() / 1000

    def set_time(self, time):
        self.media.set_time(int(time * 1000))

    def get_length(self):
        return self.media.get_length() / 1000

    def pause(self):
        self.media.pause()

    def resume(self):
        self.media.set_pause(0)

    # 是否正在播放
    def is_playing(self):
        return self.media.is_playing()

    def has_url(self):
        return bool(self.media.get_media())

    def get_position(self):
        return round(self.media.get_position(), 2)

    def set_position(self, float_val):
        return self.media.set_position(float_val)

    # 获取当前音量（0~100）
    def get_volume(self):
        return self.media.audio_get_volume()

    # 设置音量（0~100）
    def set_volume(self, volume):
        return self.media.audio_set_volume(volume)
