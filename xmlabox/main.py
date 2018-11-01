#!/usr/bin/env python
import argparse
import curses
import logging
import sys
import traceback

from logging.handlers import RotatingFileHandler

from xmlabox import __version__
from xmlabox.index import Index

FILE_FORMAT = ("[%(asctime)s.%(msecs)03d][%(pathname)s:%(funcName)s]"
               "[%(levelname)s] %(message)s")


def log_init():
    root = logging.getLogger()
    level = 'DEBUG'
    root.setLevel(level)

    log_file = '/tmp/xmlabox.log'
    log_max_size = 10 * 1024 * 1024
    log_backup_count = '3'
    fh = RotatingFileHandler(
        log_file, maxBytes=log_max_size, backupCount=log_backup_count)
    fh.setFormatter(
        logging.Formatter(fmt=FILE_FORMAT, datefmt='%Y-%m-%d %H:%M:%S'))
    root.addHandler(fh)


def main():
    log_init()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        help="show this version and exit",
        action="store_true")
    args = parser.parse_args()

    if args.version:
        print('version: %s' % __version__)
        sys.exit()

    try:
        index = Index()
        index.start()
    except Exception:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()


if __name__ == '__main__':
    main()
