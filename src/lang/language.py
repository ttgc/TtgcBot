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


from typing import Self
from enum import Enum
import os


class Language(Enum):
    EN = 'EN.lang'
    FR = 'FR.lang'

    def __new__(cls, value: str) -> Self:
        self = object.__new__(cls)
        self._value_ = os.path.join('..', 'Lang', value)

    def __init__(self, value: str) -> None:
        self._translations = {}

        with open(value, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue

                raw_split = line.split('=')
                content = raw_split[1].replace('\n', '').replace('\\n', '\n')
                self._translations[raw_split[0]] = content

    def __getitem__(self, name: str) -> str:
        return self._translations.get(
            name, self.__class__.get_default()._translations[name]
        )

    @classmethod
    def get_default(cls) -> Self:
        return cls.EN

    @classmethod
    def get(cls, code: str) -> Self:
        for lang in cls:
            if lang.name == code:
                return lang
        return cls.get_default()
