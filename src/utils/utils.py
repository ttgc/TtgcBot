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

import discord
from enum import Enum

def async_lambda(callback):
    async def _execute(*args, **kargs):
        await callback(*args, **kargs)

    return _execute

def async_conditional_lambda(check_callback, if_callback, else_callback):
    async def _execute(*args, **kwargs):
        condition = await check_callback(*args, **kwargs)
        if condition:
            await if_callback(*args, **kwargs)
        else:
            await else_callback(*args, **kwargs)

    return _execute

def try_parse_int(value: str, default_value: int = 0) -> int:
    try:
        return int(value)
    except:
        return default_value

def get_color(hexvalue: str) -> discord.Color:
    return discord.Color(int(hexvalue, 16))

class SerializableEnum(Enum):
    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)
