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
from discordui.views import View

class ButtonGroup(View):
    def __init__(self, ctx, grpid, check_callback=None, timeout=None, authorize_everyone=False, *buttons):
        super().__init__(ctx, check_callback=check_callback, timeout=timeout, authorize_everyone=authorize_everyone)
        self.buttons = []
        self.value = None
        self.grpid = grpid
        self._user_interaction = None
        if len(buttons) > 0:
            self.addrange(*buttons)

    @property
    def user_interaction():
        return self._user_interaction

    def __iadd__(self, button):
        self.addrange(button)
        return self

    def add(self, button):
        self.addrange(button)

    def addrange(self, *buttons):
        for b in buttons:
            b.custom_id = f"{self.grpid}-{len(self.buttons)}-{b.custom_id}"
            b.final = True
            b.onclick = ButtonGroup._onclick
            self.buttons.append(b)
            self.add_item(b)

    @staticmethod
    async def _onclick(btn, interaction):
        self.value = btn.custom_id
        self._user_interaction = interaction

    async def wait(self):
        result = await super().wait()
        return result, self.value, self.user_interaction
