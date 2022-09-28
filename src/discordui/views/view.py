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

import discord.ui as ui
from discordui.views import ViewResult, DefaultViewResults

class View(ui.View):
    def __init__(self, ctx, *, check_callback=None, timeout=None, authorize_everyone=False):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.check_callback = None
        self.authorize_everyone = authorize_everyone
        self._timeout_callback = None
        self._result = DefaultViewResults.NONE

    async def interaction_check(self, interaction):
        author_check = self.authorize_everyone or interaction.user == self.ctx.author
        custom_check = self.check_callback is None or self.check_callback(self.ctx, self.interaction)
        return author_check and custom_check

    @property
    def timeout_callback(self):
        return self._timeout_callback if self.timeout is not None else None

    @timeout_callback.setter
    def timeout_callback(self, callback):
        if self.timeout is not None:
            self._timeout_callback = callback

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        if isinstance(value, ViewResult):
            self._result = value
        elif isinstance(value, DefaultViewResults):
            self._result = value.value
        elif isinstance(value, int):
            self._result = ViewResult(value)
        else:
            raise TypeError(f"view result must be a ViewResult, DefaultViewResults or int but not {type(value)}")

    async def on_timeout(self):
        if self.timeout_callback is not None:
            await self.timeout_callback(self)
        await super().on_timeout()
