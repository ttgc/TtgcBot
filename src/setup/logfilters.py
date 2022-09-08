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
from utils.decorators import singleton
from setup.loglevel import LogLevel

@singleton
class Filters:
    def __init__(self):
        self += {
            "Debug": lambda record: record.levelno == LogLevel.DEBUG.value,
            "BotV3": lambda record: record.levelno == LogLevel.BOT_V3.value
        }

    def __iadd__(self, kargs):
        if not isinstance(kargs, dict):
            raise TypeError(f"Invalid type for added filter. Got {type(kargs)}. Expected: {type({})}")

        for name, filter in kargs.items():
            built_filter = type(f"{name}Filter", (logging.Filter,), {"filter": filter})
            setattr(self, name, built_filter)
