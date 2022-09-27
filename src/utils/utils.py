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
