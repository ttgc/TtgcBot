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
from exceptions.httpstatus import HTTPErrorCode

class HTTPException(commands.CommandError):
    def __init__(self, errcode, message=None):
        self.errcode = errcode
        self.message = message if message else "No more details provided"
        super().__init__(str(self))

    def __str__(self):
        return "HTTPException: Error Code {} ({})".format(self.errcode, self.message)

    def parse(self, lang):
        return HTTPErrorCode.get_code_from_int(self.errcode).toString(lang, self.message)
