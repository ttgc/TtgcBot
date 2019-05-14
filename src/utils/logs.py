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
