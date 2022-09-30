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

from discordui.views import View, ViewResult

class ButtonGroup(View):
    def __init__(self, ctx, grpid, *, check_callback=None, timeout=None, authorize_everyone=False):
        super().__init__(ctx, check_callback=check_callback, timeout=timeout, authorize_everyone=authorize_everyone)
        self.buttons = []
        self.grpid = grpid

    def __iadd__(self, button):
        return self.add(button)

    def add(self, button):
        button.custom_id = f"{self.grpid}-{len(self.buttons)}-{button.custom_id}"
        button.final = True
        button.finalize_check = None

        if not isinstance(button.view_result, ViewResult):
            button.view_result = ViewResult(len(self.buttons), is_success=True)

        self.buttons.append(button)
        return self

    def addrange(self, *buttons):
        for b in buttons:
            self.add(b)
        return self

    async def wait(self):
        timeout = await super().wait()
        return timeout
