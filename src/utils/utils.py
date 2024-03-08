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


from typing import Any
import discord
from .aliases import AsyncCallable


def async_lambda(callback: AsyncCallable[Any]) -> AsyncCallable[Any]:
    async def _execute(*args, **kargs) -> Any:
        return await callback(*args, **kargs)

    return _execute


def async_conditional_lambda(check_callback: AsyncCallable[bool], if_callback: AsyncCallable[None], else_callback: AsyncCallable[None]) -> AsyncCallable[None]:
    async def _execute(*args, **kwargs) -> None:
        condition = await check_callback(*args, **kwargs)

        if condition:
            await if_callback(*args, **kwargs)
        else:
            await else_callback(*args, **kwargs)

    return _execute


def try_parse_int(value: str, default_value: int = 0) -> int:
    try:
        return int(value)
    except ValueError:
        return default_value


def get_color(hexvalue: str) -> discord.Color:
    return discord.Color(int(hexvalue, 16))
