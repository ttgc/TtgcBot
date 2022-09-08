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

class DeprecatedException(DeprecationWarning):
    def __init__(self, fct, reason, *args, **kwargs):
        self.fct = fct
        self.args = args
        self.kwargs = kwargs
        self.reason = reason
        super().__init__(str(self))

    def __str__(self):
        invok = "{}({}, {})".format(self.fct.__name__, list(self.args), dict(self.kwargs))
        invok = invok.replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace(":", "=")
        return f"DeprecatedException: The function/class {self.fct} is deprecated\nReason: {self.reason}\nTried to invoke: {invok}"
