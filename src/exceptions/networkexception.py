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


from typing import Optional
from discord.ext import commands
from network.statuscode import HttpErrorCode


class HTTPException(commands.CommandError):
    def __init__(self, errcode: HttpErrorCode, message: Optional[str] = None):
        self.errcode = errcode
        self.message = message if message else "No more details provided"
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"HTTPException: Error Code {self.errcode} ({self.message})"

    def parse(self, lang) -> str:
        return HttpErrorCode.get_code_from_int(self.errcode).to_string(lang, self.message)
