#!/usr/bin/env python
# encoding: utf-8

import time

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

LOGIN_URL = "https://passport.ximalaya.com/page/web/login?fromUri=http://www.ximalaya.com/my/subscribed/"

driver_path = ChromeDriverManager().install()
_options = ChromeOptions()
_options.add_argument('--window-size=500,550')
_options.add_argument('--app=%s' % LOGIN_URL)
driver = webdriver.Chrome(driver_path, chrome_options=_options)

cookie = ''
while True:
    time.sleep(1)

    if driver.current_url.strip('/') == "https://www.ximalaya.com/my/subscribed":
        for i in driver.get_cookies():
            cookie += '%s=%s; ' % (i.get('name'), i.get('value'))
        break
cookie = cookie.strip(' ;')
driver.close()
print(cookie)
