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

import logging,os

class DebugFilter(logging.Filter):
    def filter(self,record):
        return record.levelno == logging.DEBUG+1

def initlogs():
    if not os.access("Logs",os.F_OK):
        os.mkdir("Logs")
    logger = logging.getLogger('discord')
    # basic handler (all)
    logging.basicConfig(level=logging.DEBUG+1)
    handler = logging.FileHandler(filename='Logs/all.log', encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    # latest logs
    handler = logging.FileHandler(filename='Logs/latest.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    # error logs
    handler = logging.FileHandler(filename='Logs/errors.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
    # debug logs
    handler = logging.FileHandler(filename='Logs/debug.log', encoding='utf-8', mode='w')
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

def checkfiles(logger,argv):
    if not os.access("ffmpeg.exe",os.F_OK):
        logger.critical("ffmpeg not found !")
        raise RuntimeError("ffmpeg not found !\nDonwload here : https://ffmpeg.org/")

    if not os.access("arial.ttf",os.F_OK) and "--no-fontcheck" not in argv:
        logger.error("Map management features need 'arial.ttf' font to work")
        raise RuntimeError("'arial.ttf' font missing\nDonwload here : https://fr.ffonts.net/Arial.font.download")

def checktest(logger,argv):
    for i in argv:
        if i.startswith("-") and not i.startswith("--") and 't' in i:
            logger.info("Test mod enabled, launching tests")
            return True
    return False
