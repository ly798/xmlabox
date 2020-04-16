class Stack(list):
    def __init__(self):
        self._collect = []

    def __len__(self):
        return len(self._collect)

    def push(self, obj):
        self._collect.append(obj)

    def pop(self):
        return self._collect.pop()

    @property
    def top(self):
        if len(self._collect) > 0:
            return self._collect[-1]
        else:
            return None

    @top.setter
    def top(self, obj):
        self._collect[-1] = obj

    @property
    def buttom(self):
        if len(self._collect) > 0:
            return self._collect[0]
        else:
            return None

    @buttom.setter
    def buttom(self, obj):
        self._collect[0] = obj

    def get_raw(self):
        return self._collect


def get_pretty_str(s, cursor, max_len=20):
    tmp = ''
    if (len(s) + cursor) > max_len:
        tmp += s[-(len(s) + cursor - max_len):]
        tmp += ' ' * (max_len - len(s))
        tmp += s[:-(len(s) + cursor - max_len)]
    else:
        tmp += ' ' * cursor
        tmp += s
        tmp += ' ' * (max_len - len(s) - cursor)

    return tmp


def sec2time(sec):
    return "%02d:%02d" % divmod(sec, 60)