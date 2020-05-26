import os
import inspect

# https://stackoverflow.com/questions/19225188/what-method-can-i-use-instead-of-file-in-python
folder_path = os.path.abspath(
    os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe()))))


def get_vjs_path():
    return os.path.join(folder_path, 'get_player_url.js')
