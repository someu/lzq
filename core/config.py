# -*- coding: UTF-8 -*-
from os import path, getcwd
from configparser import ConfigParser

from .utils import mkdir_if_not_exists

_base_path = getcwd()
_config_path = path.join(_base_path, '.config.ini')

_config = ConfigParser()
_config.read(_config_path, encoding='UTF-8')


assert path.exists(_config_path), f"配置文件 {_config_path} 不存在"

class Config():
    '''配置'''

    # 存储
    OUTPUT_DB_URL = _config.get("storage", 'db_url')
    OUTPUT_DIR = _config.get('storage', 'csv_dir')

    # 日志
    LogDirPath = path.join(_base_path, _config.get("log", "output"))
    LogLevel = _config.get("log", "level")
    LogFormat = _config.get("log", "format", raw=True)

    # 并发
    RequestWorker = _config.getint("concurrent", "request_worker")



mkdir_if_not_exists(Config.LogDirPath)
mkdir_if_not_exists(Config.OUTPUT_DIR)