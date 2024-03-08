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


import json
import os
import sys
from enum import Enum
from typing import Optional, Self, Any
from deepmerge import Merger
from utils.decorators import singleton


class Environment(Enum):
    NONE = (0, None)
    DEV = (1, "development")
    STAGING = (2, "staging")
    PROD = (3, "production")

    def __new__(cls, value: int, label: Optional[str]) -> Self:
        self = object.__new__(cls)
        self._value_ = value

    def __init__(self, value: int, label: Optional[str]) -> None:
        self._label = label

    @property
    def label(self) -> Optional[str]:
        return self._label

    def __str__(self) -> str:
        return self.label if self.label else ''

    def __eq__(self, __value: Self) -> bool:
        return self.value in (Environment.NONE.value, __value.value)

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    @classmethod
    def parse(cls, envstr: str) -> Self:
        for env in cls:
            if str(env).lower() == envstr.lower():
                return env
        return cls.NONE


@singleton
class Config:
    def __init__(self) -> None:
        merger = Merger([(dict, ["merge"])], ["override"], ["override"])
        self._dev = {}
        self._staging = {}
        self._prod = {}
        dev_path = os.path.join("..", "config", "config.development.json")
        staging_path = os.path.join("..", "config", "config.staging.json")
        prod_path = os.path.join("..", "config", "config.production.json")

        with open(os.path.join("..", "config", "config.json"), "r") as f:
            self._base = json.load(f)

        if os.access(dev_path, os.R_OK):
            with open(dev_path, "r") as f:
                self._dev = json.load(f)
        if os.access(staging_path, os.R_OK):
            with open(staging_path, "r") as f:
                self._staging = json.load(f)
        if os.access(prod_path, os.R_OK):
            with open(prod_path, "r") as f:
                self._prod = json.load(f)

        self._environment = Environment.NONE
        if len(sys.argv) > 1:
            self._environment = Environment.parse(sys.argv[1])

        self._merged = dict(self._base)
        if self._environment == Environment.DEV:
            merger.merge(self._merged, self._dev)
        if self._environment == Environment.STAGING:
            merger.merge(self._merged, self._staging)
        if self._environment == Environment.PROD:
            merger.merge(self._merged, self._prod)

    def __getitem__(self, key: str) -> Any:
        return self._merged[key]

    @property
    def env(self) -> Environment:
        return self._environment
