import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from xmlabox.data import get_chromedriver_path


class Brower:
    def __init__(self):
        #TODO: phantomjs or firefox
        #TODO: headless
        driver_path = get_chromedriver_path()
        print(driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--window-size=500,680')
        chrome_options.add_argument('--disable-images')
        self.driver = webdriver.Chrome(driver_path,
                                       chrome_options=chrome_options)

    def get_cookie(self):
        url = "https://passport.ximalaya.com/page/web/login?fromUri=http://www.ximalaya.com/my/subscribed"
        self.driver.get(url)
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