import os
import inspect
import requests
import zipfile
import tarfile
import platform
import logging
import tempfile
import stat

LOG = logging.getLogger(__name__)
system_version = platform.system()
driver_dirpath = os.path.join(os.getenv('HOME'), '.xmlabox')
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
}


def download_file_to_tmp(url):
    LOG.debug('downlond file: %s' % url)
    _, tmp_file = tempfile.mkstemp()
    res = requests.get(url, headers=headers, stream=True)
    with open(tmp_file, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    LOG.debug('downlond success: %s' % tmp_file)
    return tmp_file


def unzip_file(zip_src, dst_dir):
    LOG.debug('unzip file %s to %s' % (zip_src, dst_dir))
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')


def untar_file(tar_src, dst_dir):
    LOG.debug('untar file %s to %s' % (tar_src, dst_dir))
    try:
        tar = tarfile.open(tar_src, "r:gz")
        file_names = tar.getnames()
        for file_name in file_names:
            tar.extract(file_name, dst_dir)
        tar.close()
    except Exception:
        raise


def _get_chromedriver_path():
    driver_file = os.path.join(driver_dirpath, 'chromedriver')
    if not os.path.exists(driver_file):
        r = requests.get(
            "https://npm.taobao.org/mirrors/chromedriver/LATEST_RELEASE")
        latest_version = r.text
        # TODO: 32/64bit ?
        download_url = 'https://npm.taobao.org/mirrors/chromedriver/%s/chromedriver_%s64.zip' % (
            latest_version, system_version.lower())
        tmp_file = download_file_to_tmp(download_url)
        unzip_file(tmp_file, driver_dirpath)

    os.chmod(driver_file, stat.S_IRWXU)
    return driver_file


def _get_firefoxdriver_path():
    driver_file = os.path.join(driver_dirpath, 'geckodriver')
    if not os.path.exists(driver_file):
        # TODO: 32/64bit ? latest_version ?
        download_url = 'https://npm.taobao.org/mirrors/geckodriver/v0.26.0/geckodriver-v0.26.0-%s64.tar.gz' % system_version.lower(
        )
        tmp_file = download_file_to_tmp(download_url)
        untar_file(tmp_file, driver_dirpath)

    os.chmod(driver_file, stat.S_IRWXU)
    return driver_file


def get_browerdriver_path(brower='chrome'):
    if brower == 'chrome':
        return _get_chromedriver_path()
    elif brower == 'firefox':
        return _get_firefoxdriver_path()


if __name__ == "__main__":
    get_browerdriver_path('chrome')
    get_browerdriver_path('firefox')