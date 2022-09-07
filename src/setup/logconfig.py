#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017  Thomas PIOT
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

import logging
import os
from config import Config
from logfilters import Filters
from loglevel import LogLevel

class LogConfig:
    def __init__(self, rootdir, logconfig):
        self._logconfig = logconfig

    @property
    def mode(self):
        return 'a' if config.get("stacking", False) else 'w'

    @property
    def filepath(self):
        return os.paths.join(rootdir, config["filename"])

    @property
    def enabled(self):
        return config.get("enabled", True)

    @property
    def minlevel(self):
        return LogLevel.parse(config.get("minlevel", None))

    @property
    def filter(self):
        return getattr(Filters(), config.get("filter", ""), None)

    def to_handler(self, *, encoding='utf-8'):
        handler = logging.FileHandler(filename=self.filepath, encoding=encoding, mode=self.mode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

        if minlevel is not None:
            handler.setLevel(self.minlevel)
        if filter is not None:
            handler.addFilter(self.filter)

        return handler

    @classmethod
    def all(cls):
        self._logs = []
        for i in Config.get('logs')['list']:
            self._logs.append(cls(i))
        return self._logs
