#!usr/bin/env python3.7
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

import logging, os
from src.utils.config import *

class DebugFilter(logging.Filter):
    def filter(self,record):
        return record.levelno == logging.DEBUG+1

def initlogs():
    config = Config()["logs"]
    if not os.access(config["directory"], os.F_OK):
        os.mkdir(config["directory"])
    logger = logging.getLogger('discord')
    logging.basicConfig(level=logging.DEBUG+1)

    # basic handler (all)
    if config["all"]["enabled"]:
        logmode = 'a' if config["all"]["stacking"] else 'w'
        logfile = "{}/{}".format(config["directory"], config["all"]["filename"])
        handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode=logmode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

    # latest logs
    if config["latest"]["enabled"]:
        logmode = 'a' if config["latest"]["stacking"] else 'w'
        logfile = "{}/{}".format(config["directory"], config["latest"]["filename"])
        handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode=logmode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    # error logs
    if config["errors"]["enabled"]:
        logmode = 'a' if config["errors"]["stacking"] else 'w'
        logfile = "{}/{}".format(config["directory"], config["errors"]["filename"])
        handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode=logmode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)

    # debug logs
    if config["debug"]["enabled"]:
        logmode = 'a' if config["debug"]["stacking"] else 'w'
        logfile = "{}/{}".format(config["directory"], config["debug"]["filename"])
        handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode=logmode)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        handler.addFilter(DebugFilter())
        logger.addHandler(handler)

    return logger

def initdirs(logger):
    if not os.access("Hentai/",os.F_OK):
        os.mkdir("Hentai")
        logger.info("Create Hentai directory")

    if not os.access("Music/",os.F_OK):
        os.mkdir("Music")
        logger.info("Create Music directory")

def checkfiles(logger):
    config = Config()

    if not os.access("ffmpeg.exe",os.F_OK) and config["vocal"]:
        logger.critical("ffmpeg not found !")
        raise RuntimeError("ffmpeg not found !\nDonwload here : https://ffmpeg.org/")

    if config["fonts"]["check"]:
        if not os.access(config["fonts"]["directory"], os.F_OK):
            logger.error("Fonts directory not found")
            raise RuntimeError("Fonts directory not found")
        for key, font in config["fonts"]["list"].items():
            if not os.access("{}/{}".format(config["fonts"]["directory"], font), os.F_OK):
                logger.error("Font '%s' for key '%s' was not found in the font directory", font, key)
                raise RuntimeError("Font not found ! Check 'errors.log'")
