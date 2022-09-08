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

import json
import os
import sys
from deepmerge import Merger
from utils.decorators import singleton
from enum import Enum

class Environment(Enum):
    NONE = (0, None)
    DEV = (1, "development")
    STAGING = (2, "staging")
    PROD = (3, "production")

    @classmethod
    def parse(cls, envstring):
        for i in cls:
            if i.label == envstring:
                return i
        return cls.NONE

    @property
    def id(self):
        return self.value[0]

    @property
    def label(self):
        return self.value[1]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == Environment.NONE.id or self.id == other.id

    def __ne__(self, other):
        return not (self == other)

@singleton
class Config:
    merger = Merger([(dict, ["merge"])], ["override"], ["override"])

    def __init__(self):
        self._dev = {}
        self._staging = {}
        self._prod = {}

        with open("config/config.json", "r") as f:
            self._base = json.load(f)

        if os.access("config/config.development.json", os.R_OK):
            with open("config/config.development.json", "r") as f:
                self._dev = json.load(f)
        if os.access("config/config.staging.json", os.R_OK):
            with open("config/config.staging.json", "r") as f:
                self._staging = json.load(f)
        if os.access("config/config.production.json", os.R_OK):
            with open("config/config.production.json", "r") as f:
                self._prod = json.load(f)

        self._environment = Environment.NONE
        if len(sys.argv) > 1:
            self._environment = Environment.parse(sys.argv[1])

        self._merged = dict(self._base)
        if self._environment == Environment.DEV:
            self.merger.merge(self._merged, self._dev)
        if self._environment == Environment.STAGING:
            self.merger.merge(self._merged, self._staging)
        if self._environment == Environment.PROD:
            self.merger.merge(self._merged, self._prod)

    def __getitem__(self, key):
        return self._merged[key]

    @property
    def env(self):
        return self._environment
