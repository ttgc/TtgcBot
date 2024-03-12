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


from typing import Optional, Self
from enum import IntEnum
import logging
import os
from utils.decorators import call_once
from .config import Config


class LogFilter(IntEnum):
    DEBUG = logging.DEBUG + 1
    BOTV4 = logging.DEBUG + 2
    BOTV3 = logging.DEBUG + 2

    def __call__(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.value

    @classmethod
    def parse(cls, filter_name: str) -> Optional[Self]:
        for filter in cls:
            if filter.name.lower() == filter_name.lower():
                return filter
        return None

class LogConfig:
    _level_map = {
        'info': logging.INFO,
        'debug': logging.DEBUG + 1,
        'warning': logging.WARN,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
        'v4': logging.DEBUG + 2,
        'min': logging.DEBUG
    }

    def __init__(self, rootdir: str, **config) -> None:
        self._rootdir = rootdir
        self._logconfig = config

    @property
    def mode(self) -> str:
        return 'a' if self._logconfig.get("stacking", False) else 'w'

    @property
    def filepath(self) -> str:
        return os.path.join(self._rootdir, self._logconfig["filename"])

    @property
    def enabled(self) -> bool:
        return self._logconfig.get("enabled", True)

    @property
    def minlevel(self) -> int:
        return self._level_map.get(self._logconfig.get("minlevel", None), logging.DEBUG + 1)

    @property
    def filter(self) -> Optional[LogFilter]:
        return LogFilter.parse(self._logconfig.get("filter", ""))

    def to_handler(self, *, encoding='utf-8') -> logging.Handler:
        handler = logging.FileHandler(filename=self.filepath, encoding=encoding, mode=self.mode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

        if self.minlevel:
            handler.setLevel(self.minlevel)
        if self.filter:
            handler.addFilter(self.filter)

        return handler

    @classmethod
    def _register_levels(cls) -> None:
        for lvlname, lvlval in cls._level_map.items():
            if lvlval % 10 != 0:
                logging.addLevelName(lvlval, lvlname.upper())

    @classmethod
    @call_once()
    def load_all(cls) -> list[Self]:
        cls._register_levels()
        config = Config()['logs']
        return [cls(config['directory'], **cfg) for cfg in config['list']]
