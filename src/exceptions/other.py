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

from discord.ext import commands

class InternalCommandError(commands.CommandError): pass

class NotBoundException(InternalCommandError):
    def __init__(self, obj, msg):
        super().__init__(f"{obj} not bound: {msg}")
        self._obj = obj

    @property
    def obj(self):
        return self._obj

class RaisedExceptionCommandError(InternalCommandError):
    def __init__(self, inner: Exception):
        super().__init__(f"Command raised {type(inner).__name__}: {inner}")
