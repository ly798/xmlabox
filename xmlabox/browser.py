import logging
import time
import subprocess
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver import FirefoxOptions

from xmlabox.data import get_chromedriver_path, get_firefoxdriver_path

LOG = logging.getLogger(__name__)
LOGIN_URL = "https://passport.ximalaya.com/page/web/login?fromUri=http://www.ximalaya.com/my/subscribed"


class Brower:
    def __init__(self):
        #TODO: headless
        self._brower = self._get_brower()
        LOG.debug(self._brower)
        if self._brower == 'chrome':
            driver_path = get_chromedriver_path()
            _options = ChromeOptions()
            _options.add_argument('--window-size=500,550')
            # _options.add_argument('--disable-images')
            _options.add_argument('--app=%s' % LOGIN_URL)
            self.driver = webdriver.Chrome(driver_path,
                                           chrome_options=_options)
        elif self._brower == 'firefox':
            driver_path = get_firefoxdriver_path()
            _options = FirefoxOptions()
            _options.add_argument('--width=500')
            _options.add_argument('--height=630')
            # _options.set_preference("permissions.default.image", 2)
            _options.set_preference("browser.urlbar.update1", False)
            self.driver = webdriver.Firefox(executable_path=driver_path,
                                            options=_options)
            self.driver.get(LOGIN_URL)
        else:
            #TODO: phantomjs ?
            pass

    def _get_brower(self):
        gs1, _ = subprocess.getstatusoutput('google-chrome-stable --version')
        gs2, _ = subprocess.getstatusoutput('google-chrome --version')
        if gs1 == 0 or gs2 == 0:
            return 'chrome'
        fs, _ = subprocess.getstatusoutput('firefox --version')
        if fs == 0:
            return 'firefox'
        return None

    def get_cookie(self):
        cookie = ''
        while True:
            time.sleep(1)
            if self.driver.current_url == "https://www.ximalaya.com/my/subscribed/":
                for i in self.driver.get_cookies():
                    cookie += '%s=%s; ' % (i.get('name'), i.get('value'))
                break
        cookie = cookie.strip(' ;')
        self.driver.close()
        return cookie


if __name__ == "__main__":
    brower = Brower()
    brower.get_cookie()