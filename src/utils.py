import glob
import itertools
import os
import time
import shutil
from datetime import datetime

from decouple import config

from src.constants import JobAnalytics
from .log import setup_custom_logger

LOGGER = setup_custom_logger(__name__)
MAX_DAYS_TEMP_FILES = config(f'MAX_DAYS_TEMP_FILES', default=30, cast=int)


def _raise(ex):
    raise ex


def utf8len(s):
    return len(s.encode('utf-8'))


def get_path_temp_from_report(_report, _file=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_data = os.path.join(base_dir, 'temp')
    if not os.path.isdir(dir_data):
        os.mkdir(dir_data)
    dir_report = os.path.join(dir_data, _report)
    if not os.path.isdir(dir_report):
        os.mkdir(dir_report)
    if _file is None:
        return dir_report
    return os.path.join(dir_report, _file)


def get_size_file(_path):
    return os.path.getsize(_path)


def remove_old_temp_files(_report, _days=None):
    try:
        _days = MAX_DAYS_TEMP_FILES if _days is None else _days
        _path_report = get_path_temp_from_report(_report)
        LOGGER.info(f"_days ago: {_days}, _path_report: {_path_report}")
        _time_days_ago = time.time() - (_days * 86400)
        LOGGER.info(f"datetime max to remove old files: {datetime.fromtimestamp(_time_days_ago)}")

        list_of_files = filter(os.path.isfile, glob.glob(os.path.join(_path_report, '*.json')))
        list_of_files = sorted(list_of_files, key=os.path.getmtime, reverse=False)

        LOGGER.info(f"size files total: {len(list_of_files)}")

        _del_files = 0
        for i in list_of_files:
            _path = os.path.join(_path_report, i)
            _stat = os.stat(_path)
            if _stat.st_mtime <= _time_days_ago:
                if os.path.isfile(_path):
                    os.remove(_path)
                    LOGGER.info(f"file removed -> st_mtime: '{datetime.fromtimestamp(_stat.st_mtime)}', _path: '{_path}'")
                    _del_files += 1
                # else:
                #     shutil.rmtree(_path)
                #     LOGGER.info(f"dir remove: {_path}")
            else:
                LOGGER.info(f"file next to begin remove -> st_mtime: '{datetime.fromtimestamp(_stat.st_mtime)}', _path: '{_path}'")
                LOGGER.info("exit loop files to remove")
                break
        LOGGER.info(f"files removed: {_del_files}")
    except Exception as ex:
        LOGGER.exception(ex)


def chunked_iterable(_iterable, _size):
    """ https://alexwlchan.net/2018/12/iterating-in-fixed-size-chunks/ """
    _it = iter(_iterable)
    while True:
        _chunk = tuple(itertools.islice(_it, _size))
        if not _chunk:
            break
        yield _chunk


def chunked_iterable2(_list, _n):
    """ https://www.geeksforgeeks.org/break-list-chunks-size-n-python/ """
    for i in range(0, len(_list), _n):
        yield _list[i:i + _n]


if __name__ == '__main__':
    remove_old_temp_files(JobAnalytics.TEST)
