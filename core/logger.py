# -*- coding: UTF-8 -*-

import logging
from .config import Config
from os import path
from datetime import datetime


def get_logger(name="LZQ"):
    """设置日志logger"""
    logger = logging.getLogger(name)
    formatter = logging.Formatter(fmt=Config.LogFormat)

    # 控制台输出
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(Config.LogLevel)
    logger.addHandler(sh)

    # 日志文件输出 logs/2022-02-02.log
    log_file = f'{datetime.now().strftime("%Y-%m-%d")}.log'
    fh = logging.FileHandler(path.join(Config.LogDirPath, log_file), encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel("DEBUG")
    logger.addHandler(fh)

    return logger


logger = get_logger()
