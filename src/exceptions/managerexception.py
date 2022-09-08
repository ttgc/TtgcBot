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
from network.statuscode import HTTPErrorCode

class ManagerException(commands.CommandError):
    def __init__(self, message="Manager exception occured", **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(str(self))

    def __getitem__(self, item):
        return self.kwargs.get(item, None)

    def __str__(self):
        return f"ManagerException: {self.message} (with kwargs {self.kwargs})"

class DatabaseException(ManagerException):
    def __str__(self):
        return f"DatabaseException: {self.message} (with kwargs {self.kwargs})"

class APIException(ManagerException):
    def __str__(self):
        return "APIException: {self.message} (with kwargs {self.kwargs})"

    def parse(self, lang):
        return HTTPErrorCode.get_code_from_int(self.kwargs.get("code", 502)).toString(lang, None, **self.kwargs)
