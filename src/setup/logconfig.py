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
from setup.config import Config
from setup.logfilters import Filters
from setup.loglevel import LogLevel
from utils.decorators import call_once

class LogConfig:
    def __init__(self, rootdir, logconfig):
        self._rootdir = rootdir
        self._logconfig = logconfig

    @property
    def mode(self):
        return 'a' if self._logconfig.get("stacking", False) else 'w'

    @property
    def filepath(self):
        return os.path.join(self._rootdir, self._logconfig["filename"])

    @property
    def enabled(self):
        return self._logconfig.get("enabled", True)

    @property
    def minlevel(self):
        return LogLevel.parse(self._logconfig.get("minlevel", None))

    @property
    def filter(self):
        return getattr(Filters(), self._logconfig.get("filter", ""), None)

    def to_handler(self, *, encoding='utf-8'):
        handler = logging.FileHandler(filename=self.filepath, encoding=encoding, mode=self.mode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

        if self.minlevel is not None:
            handler.setLevel(self.minlevel.value)
        if self.filter is not None:
            handler.addFilter(self.filter)

        return handler

    @classmethod
    def all(cls):
        logs = []
        config = Config()['logs']
        for i in config['list']:
            logs.append(cls(config['directory'], i))
        return logs


@call_once()
def get_logger():
    config = Config()["logs"]

    if not os.access(config["directory"], os.F_OK):
        os.mkdir(config["directory"])

    logger = logging.getLogger('discord')
    logging.basicConfig(level=LogLevel.MIN.value)

    for config in LogConfig.all():
        print(config.filepath, config.filter)
        logger.addHandler(config.to_handler())

    logger.info("Logger configured")
    return logger
