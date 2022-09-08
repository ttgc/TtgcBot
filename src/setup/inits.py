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
from setup.config import Config, Environment
from setup.logfilters import Filters
from setup.loglevel import LogLevel
from setup.logconfig import LogConfig, get_logger
from utils.decorators import call_once

@call_once()
def _initdirs(logger):
    config = Config()["directories"]

    if not os.access(config["nsfw"], os.F_OK):
        os.mkdir(config["nsfw"])
        logger.info("Create NSFW directory")

    if not os.access(config["jokes"], os.F_OK):
        os.mkdir(config["jokes"])
        with open(os.path.join(config["jokes"], "joke-FR.txt"), "w"): pass
        with open(os.path.join(config["jokes"], "joke-EN.txt"), "w"): pass
        with open(os.path.join(config["jokes"], "nsfw-FR.txt"), "w"): pass
        with open(os.path.join(config["jokes"], "nsfw-EN.txt"), "w"): pass
        logger.info("Create Jokes directory and files")

    if not os.access("Lang/", os.F_OK):
        os.mkdir("Lang")

@call_once(True)
def init():
    logger = get_logger()
    _initdirs(logger)
    logger.info("Init done")
    logger.log(LogLevel.DEBUG.value, "test")
    return logger
