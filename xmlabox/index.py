import curses
import copy
import logging
import time
import _thread
import os

import vlc

from wcwidth import wcswidth

from xmlabox.utils import Stack, get_pretty_str, sec2time
from xmlabox.ximalaya import ximalaya
from xmlabox.storage import Storage
from xmlabox.base import Item, User
from xmlabox.player import Player
from xmlabox.browser import Brower

LOG = logging.getLogger(__name__)
'''
menu type:
0 -> home菜单
1 -> 专辑菜单
2 -> 专辑章节菜单
'''
# 已登录的可选择项
LOGINED_ITEMS = [
    Item('local_history_list', '本地历史', 'display_local_history_list'),
    Item('history_list', '历史记录', 'display_history_list'),
    Item('collect_list', '我的收藏', 'display_collect_list'),
    Item('logout', '退出登陆', 'user_logout'),
    Item('help', '帮助(?)', 'display_help'),
]
# 未登录的可选择项
LOGOUTED_ITEMS = [
    Item('login', '登录', 'user_login'),
    Item('help', '帮助(?)', 'display_help'),
]


class Index():
    """
    分布:
    ---------------------------------
    |喜马拉雅                  用户名  |   <------- header
    ---------------------------------
    |  ------------                  |
    |  | 菜单列表   |                 |
    |  ------------        -------   |   <------- body
    |                      | 帮助 |   |
    |                      -------   |
    |   -------------------------    |
    |   |         播放器         |    |
    |   -------------------------    |
    |---------------------------------
    |secect: -1                日志   |   <------- footer
    ----------------------------------
    """
    def __init__(self):
        LOG.info('start ximalayabox...')
        # 显示参数
        self._x = 10  #起点x
        self._y = 5  #起点y
        self.weight = 60  # 宽度
        self.height = 31

        self._init_curses()

        self.islogin = False
        self.storage = Storage()
        self.user = User(None)
        # 正在播放的章节对象
        self.current_play = self.storage.current_play

        self._valid_login()

        # 选择的菜单项编号
        self.select_index = 0
        # 菜单项
        self.menu_stack = Stack()
        if self.islogin:
            self.menu_stack.push({'type': 0, 'items': LOGINED_ITEMS})
        else:
            self.menu_stack.push({'type': 0, 'items': LOGOUTED_ITEMS})
        # 分页
        self.pages = 1
        self.page_num = 1
        # input key
        self.key = '0'
        # 右下角显示的log
        self.log_string = ''
        self.ishelp = False
        self.isexit = False

        self._init_player()

        # 是否上/下一首
        self.is_change = 0

        _thread.start_new_thread(self._bg, ())

        # 分页类型: 0 -> history; 1 -> track 分页类型不同，所调用的获取下一页内容方法不同
        self.page_type = 0

        # 是否登录中
        self.logining = False
        self.logining_cursor = 3

    def _init_player(self):
        LOG.debug('init vlc player')
        self.player = Player()
        LOG.debug('set vlc volume: %s' % self.storage.volume)
        # 新建vlc对象后在未播放前都获取的音量均为0，从之前的记录中获取并设置
        self.player.set_volume(self.storage.volume)
        LOG.debug('set vlc rate: %s' % self.storage.rate)
        self.player.set_rate(self.storage.rate)
        self.player.add_callback(vlc.EventType.MediaPlayerEndReached,
                                 self.play_next_cb)
        self.player.add_callback(vlc.EventType.MediaPlayerPositionChanged,
                                 self.update_time)

    def _valid_login(self):
        LOG.debug('get cookie: %s' % self.storage.cookie)
        if self.storage.cookie:
            self.ximalaya = ximalaya(self.storage.cookie)
            self.user = self.ximalaya.get_current_user()
            if self.user.is_login():
                self.islogin = True

    def _bg(self):
        while True:
            # 是否上/下一首
            if self.is_change == 1:
                self._play(isnew=True)
                self.is_change = 0
            # 标题移动
            if self.current_play and self.player.is_playing():
                self.current_play.cursor = self.current_play.cursor + 1 \
                    if self.current_play.cursor < 19 else 0
            # 音量
            self.storage.volume = self.player.get_volume()
            self.storage.rate = self.player.get_rate()

            time.sleep(1)

    @vlc.callbackmethod
    def play_next_cb(self, event):
        LOG.debug('play next...')
        self.current_play = self.ximalaya.get_next_track(self.current_play.id)
        self.is_change = 1
        self.log_string = '播放下一首'

    @vlc.callbackmethod
    def play_pre_cb(self, event):
        LOG.debug('play pre...')
        self.current_play = self.ximalaya.get_pre_track(self.current_play.id)
        self.is_change = 1
        self.log_string = '播放上一首'

    @vlc.callbackmethod
    def update_time(self, event):
        if not self.current_play.length:
            self.current_play.length = self.player.get_length()
        self.current_play.time = self.player.get_time()
        self.current_play.position = self.player.get_position()

    def _adjust_postion(self):
        height, width = self.screen.getmaxyx()
        self._x = (width // 2 - self.weight // 2) - 1
        self._y = height // 2 - self.height // 2

    def _init_curses(self):
        # 初始化一个终端
        self.screen = curses.initscr()
        # 开启键盘模式
        self.screen.keypad(1)
        self.screen.nodelay(1)
        curses.noecho()
        curses.cbreak()
        curses.start_color()

        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)

    @property
    def current_meun_type(self):
        top = self.menu_stack.top
        if top and isinstance(top, dict):
            return top.get('type', 0)
        return 0

    @property
    def current_items(self):
        top = self.menu_stack.top
        if top and isinstance(top, dict):
            return top.get('items', [])
        return []

    def _modify_current_items(self, items):
        top = self.menu_stack.top
        if top and isinstance(top, dict):
            top['items'] = items

    def save_history(self):
        LOG.debug('save history')
        if not self.current_play:
            LOG.warn('cannot save the current play object to history file')
            return
        self.storage.add_current_play(self.current_play)
        self.storage.volume = self.player.get_volume()
        self.storage.rate = self.player.get_rate()
        self.storage.save()
        LOG.debug('successfully saved the current play object to history file')
        #TODO: 未生效
        self.ximalaya.commit_process(self.current_play.id,
                                     self.current_play.time)

    def display_info(self, display_str, x, y, colorpair=2):
        self.screen.addstr(y, x, display_str, curses.color_pair(colorpair))

    def display_header(self):
        x = self._x
        y = self._y
        self.display_info('喜马拉雅', x, y, 1)

        if self.user:
            userstr = '用户: %s' % self.user.username
            tmp_x = x + self.weight - wcswidth(userstr)
            self.display_info(userstr, tmp_x, y, 1)

        self.display_info('-' * self.weight, x, y + 1)
        nar_str = ''
        for obj in self.menu_stack.get_raw():
            if obj.get('type') == 0:
                nar_str += 'Home'
            elif obj.get('type') == 1:
                nar_str += ' / Album'
            elif obj.get('type') == 2:
                nar_str += ' / Chapter'
            elif obj.get('type') == 3:
                nar_str += ' / Exit'
        self.display_info(nar_str, x, y + 2)
        self.display_info('-' * self.weight, x, y + 3)

    def display_body(self):
        self._display_menu()
        self._display_comment()
        if self.ishelp:
            self._display_help()
        if self.isexit:
            self._display_exit_window()

        if self.islogin:
            self._display_pagination()
            self._display_player()

    def _display_comment(self):
        x = self._x + 5
        y = self._y + 5
        if self.current_items:
            self.display_info(
                getattr(self.current_items[self.select_index], 'comment'), x,
                y, 2)

    def _display_pagination(self):
        x = self._x + 5
        y = self._y + 18
        self.display_info('--- %s/%s ---' % (self.page_num, self.pages), x, y,
                          2)

    def _display_menu(self):
        x = self._x + 5
        y = copy.deepcopy(self._y + 7)

        # 登录中
        if self.logining:
            self.display_info('登录中%s' % ('.' * self.logining_cursor), x, y)
            return

        if not len(self.current_items):
            self.display_info('什么都没有~~', x, y)

        for index in range(len(self.current_items)):
            option = self.current_items[index]
            if self.select_index == index:
                self.display_info('-> %s: %s' % (index, option.display_name),
                                  x - 3, y, 2)
            else:
                self.display_info('%s: %s' % (index, option.display_name), x,
                                  y, 5)
            y += 1

    def _display_player(self):
        "进度条"
        x = self._x + 2
        y = self._y + 22
        progress_bar_len = 40
        play_progress_bar_len = 0
        if self.current_play:
            play_progress_bar_len = int(progress_bar_len *
                                        self.current_play.position)

            cursor = self.current_play.cursor
            max_len = 20
            play_display_name = self.current_play.name
            # play_display_name 长度不能大于 max_len
            if len(play_display_name) >= max_len:
                play_display_name = play_display_name[:19]

            self.display_info(
                '\u266a %s' %
                get_pretty_str(play_display_name, cursor, max_len), x, y, 5)

        self.display_info('[\u2261 速率: %s]' % round(self.storage.rate, 1),
                          x + 42, y - 1, 5)
        self.display_info('[\u25c0 音量: %s]' % self.storage.volume, x + 42, y,
                          5)
        self.display_info(
            '[%s%s][%s/%s]' %
            ('=' * play_progress_bar_len, '-' *
             (progress_bar_len - play_progress_bar_len),
             sec2time(getattr(self.current_play, 'time', 0)),
             sec2time(getattr(self.current_play, 'length', 0))), x, y + 1, 5)

    def _display_exit_window(self):
        x = self._x + 15
        y = self._y + 10
        self.display_info('-' * 26, x, y, 3)
        self.display_info('| 确认退出?              |', x, y + 1, 3)
        self.display_info('|%s|' % (' ' * 24), x, y + 2, 3)
        self.display_info('| 取消(ESC)  确认(ENTER) |', x, y + 3, 3)
        self.display_info('-' * 26, x, y + 4, 3)

    def _display_help(self):
        x = self._x + 27
        y = self._y + 7
        self.display_info('-' * 27, x, y - 1, 5)
        help_items = [
            ('?', '帮助'),
            ('Backspace', '返回上一步'),
            ('+', '音量增加'),
            ('-', '音量减小'),
            (')', '速率增加'),
            ('(', '速率减小'),
            ('->', '快进'),
            ('<-', '快退'),
            ('>', '上一首'),
            ('<', '下一首'),
            ('q', '退出'),
        ]
        for k, v in help_items:
            self.display_info(
                '|%s%s%s%s%s|' %
                (' ' * (10 - wcswidth(k)), k, ' ' * 5, v, ' ' *
                 (10 - wcswidth(v))), x, y, 5)
            y += 1
        self.display_info('-' * 27, x, y, 5)

    def display_footer(self):
        x = self._x
        y = self._y + 25
        self.display_info('-' * self.weight, x, y)
        self.display_info(self.key, x, y + 1, 1)
        log_tmp_x = x + self.weight - wcswidth(self.log_string)
        self.display_info(self.log_string, log_tmp_x, y + 1, 1)

    def _pre_page(self):
        if self.current_meun_type == 0:
            return
        LOG.debug('skip to previous page')
        if self.page_num == 1:
            self.log_string = '已经是第一页'
        else:
            self.page_num -= 1
            if self.page_type == 0:
                self.display_history_list(True)
            else:
                self.display_chapter_list(self.select_item, True)

    def _next_page(self):
        if self.current_meun_type == 0:
            return
        LOG.debug('skip to next page')
        if self.page_num == self.pages:
            self.log_string = '已经是最后一页'
        else:
            self.page_num += 1
            if self.page_type == 0:
                self.display_history_list(True)
            else:
                self.display_chapter_list(self.select_item, True)

    def start(self):
        while True:
            self.screen.timeout(500)
            self.screen.clear()
            self.screen.clrtobot()
            curses.noecho()

            self._adjust_postion()

            self.display_header()
            self.display_body()
            self.display_footer()

            key = self.screen.getch()
            self.key = '%s' % key

            # 下
            if key == ord('j') or key == 258:
                if not self.select_index == len(self.current_items) - 1:
                    self.select_index += 1
                else:
                    self._next_page()
            # 上
            elif key == ord('k') or key == 259:
                if not self.select_index == 0:
                    self.select_index -= 1
                else:
                    self._pre_page()
            # 返回上一步
            elif key == 263:
                self.back_step()
            # 帮助
            elif key == ord('?'):
                self.display_help()
            # 选择
            elif key == 10:
                if self.current_items:
                    self.select_item = self.current_items[self.select_index]
                # 如果是首页
                if self.current_meun_type == 0:
                    LOG.debug('select index: %s' % self.select_item)
                    func = getattr(self.select_item, 'func')
                    self.log_string = 'exec function: %s' % func
                    getattr(self, func)()
                # 如果是专辑列表
                elif self.current_meun_type == 1:
                    LOG.debug('select chapter: %s' % self.select_item)
                    self.display_chapter_list(self.select_item)
                # 如果是章节列表
                elif self.current_meun_type == 2:
                    LOG.debug('select meun: %s' % self.select_item)
                    self.current_play = self.select_item
                    self.log_string = 'play %s' % self.select_item.display_name
                    self._play(isnew=True)
                elif self.current_meun_type == 3:
                    LOG.debug('exit')
                    if self.islogin:
                        self.save_history()
                    break

            # 退出
            elif key == ord('q'):
                if not self.isexit:
                    self.isexit = True
                    self.menu_stack.push({'type': 3, 'items': {}})

            # 取消
            elif key == 27:
                if self.isexit:
                    self.isexit = False
                    self.menu_stack.pop()

            # 上一页
            elif key == ord('p') or key == curses.KEY_PPAGE:
                self._pre_page()
            # 下一页
            elif key == ord('n') or key == curses.KEY_NPAGE:
                self._next_page()

            elif key == 32 or key == ord(' '):
                if self.current_play:
                    if self.player.is_playing():
                        self.player.pause()
                        self.save_history()
                    else:
                        if self.player.has_url():
                            self.player.resume()
                        else:
                            self._play()
                else:
                    self.log_string = '无法播放'

            # 音量
            elif key == ord('+') or key == 43:
                if self.storage.volume < 100:
                    self.player.set_volume(self.storage.volume + 2)
            elif key == ord('-') or key == 95:
                if self.storage.volume > 0:
                    self.player.set_volume(self.storage.volume - 2)

            # 速率
            elif key == ord(')') or key == 41:
                if self.storage.rate < 3:
                    self.player.set_rate(self.storage.rate + 0.1)
            elif key == ord('(') or key == 40:
                if self.storage.rate > 0:
                    self.player.set_rate(self.storage.rate - 0.1)

            # 下一首
            elif key == ord('>') or key == 62:
                self.play_next_cb(event=None)
            # 上一首
            elif key == ord('<') or key == 60:
                self.play_pre_cb(event=None)

            # 快进/快退
            elif key == 261:
                self.player.set_time(self.current_play.time + 3)
            elif key == 260:
                self.player.set_time(self.current_play.time - 3)

            self.screen.refresh()

        curses.endwin()

    def user_logout(self):
        self.islogin = False
        self.user = User(None)
        self.storage.cookie = None
        self.storage.save()
        self.menu_stack.top = {'type': 0, 'items': LOGOUTED_ITEMS}
        self.select_index = 0

    def user_login(self):
        _thread.start_new_thread(self._login, ())

    def _login(self):
        self.logining = True
        try:
            cookie = Brower().get_cookie(self)
            self.storage.cookie = cookie
            self.storage.save()
            self._valid_login()
            if self.islogin:
                self.menu_stack.top = {'type': 0, 'items': LOGINED_ITEMS}
                self.select_index = 0
        finally:
            self.logining = False

    def display_collect_list(self):
        """显示收藏列表"""
        # 获取收藏
        collect_list = self.ximalaya.get_subscribe()
        self.menu_stack.push({'type': 1, 'items': collect_list})
        self.select_index = 0

    def display_help(self):
        """显示帮助"""
        # 反转
        self.ishelp = not self.ishelp

    def back_step(self):
        """返回上一步"""
        if len(self.menu_stack) > 1:
            self.menu_stack.pop()
            self.select_index = 0
        self.log_string = '返回上一步'

    def display_history_list(self, is_page=False):
        """显示历史记录"""
        history = self.ximalaya.get_history(page_num=self.page_num)
        self.pages = history.get('pages')
        self.page_type = 0
        # 如果不是翻页
        if not is_page:
            self.menu_stack.push({'type': 2, 'items': history.get('data')})
        else:
            # 翻页只修改数据
            self._modify_current_items(history.get('data'))
        self.select_index = 0

    def display_local_history_list(self):
        """显示本地历史记录"""
        history = self.storage.local_history
        self.menu_stack.push({'type': 2, 'items': history})
        self.select_index = 0

    def display_chapter_list(self, album, is_page=False):
        """显示专辑的章节记录"""
        tracks = self.ximalaya.get_track_list(album.id, page_num=self.page_num)
        self.pages = tracks.get('pages')
        self.page_type = 1
        # 如果不是翻页
        if not is_page:
            self.menu_stack.push({'type': 2, 'items': tracks.get('data')})
        else:
            # 翻页只修改数据
            self._modify_current_items(tracks.get('data'))
        self.select_index = 0

    def _play(self, isnew=False):
        if not self.current_play.src:
            self.current_play.src = self.ximalaya.get_track_src(
                self.current_play.id)
        self.player.set_uri(self.current_play.src)
        LOG.debug('start play: %s, src: %s, time: %s, length: %s, ret: %s' %
                  (self.current_play.name, self.current_play.src,
                   self.current_play.time, self.current_play.length,
                   self.player.play()))
        if not isnew:
            self.player.set_time(self.current_play.time)
        self.save_history()
