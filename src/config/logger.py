#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2024  Thomas PIOT
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program. If not, see <http://www.gnu.org/licenses/>


from typing import Optional
import os
import sys
import logging
from utils.decorators import call_once
from utils import ExitCode
from .logconfig import LogConfig
from .config import Config


@call_once()
def _get_logger_internal() -> logging.Logger:
    config = Config()["logs"]

    if not os.access(config["directory"], os.F_OK):
        os.mkdir(config["directory"])

    logger = logging.getLogger('discord')
    logging.basicConfig(level=logging.DEBUG + 1)
    logger.setLevel(logging.DEBUG + 1)

    for config in LogConfig.load_all():
        logger.addHandler(config.to_handler())

    logger.info("Logger configured")
    return logger


def get_logger() -> logging.Logger:
    logger = _get_logger_internal()

    if logger.getEffectiveLevel() > logging.DEBUG + 1:
        logger.setLevel(logging.DEBUG + 1)

    return logger


class Log:
    def __init__(self) -> None:
        raise RuntimeError('Cannot instantiate this class')

    @staticmethod
    def debug(msg: str, *args) -> None:
        get_logger().log(logging.DEBUG + 1, msg, *args)

    @staticmethod
    def debug_v4(msg: str, *args) -> None:
        get_logger().log(logging.DEBUG + 2, msg, *args)

    @staticmethod
    def info(msg: str, *args) -> None:
        get_logger().info(msg, *args)

    @staticmethod
    def warn(msg: str, *args) -> None:
        get_logger().warn(msg, *args)

    @staticmethod
    def error(msg: str, *args) -> None:
        get_logger().error(msg, *args)

    @staticmethod
    def critical(msg: str, *args, kill_code: Optional[ExitCode] = ExitCode.DEFAULT_CRITICAL_EXCEPTION) -> None:
        get_logger().critical(msg, *args)

        if kill_code is not None:
            sys.exit(kill_code)
