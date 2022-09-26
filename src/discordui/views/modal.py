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

class Modal(ui.Modal):
    def __init__(self, ctx, title, *, check_callback=None, timeout=None, id=None, onsubmit=None):
        super().__init__(title=title, timeout=timeout, custom_id=id if id is not None else title)
        self.ctx = ctx
        self.check_callback = None
        self._timeout_callback = None
        self._user_interaction = None
        self._onsubmit = onsubmit

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author and (self.check_callback is None or self.check_callback(self.ctx, self.interaction))

    @property
    def timeout_callback(self):
        return self._timeout_callback if self.timeout is not None else None

    @timeout_callback.setter
    def timeout_callback(self, callback):
        if self.timeout is not None:
            self._timeout_callback = callback

    @property
    def onsubmit(self):
        return self._onsubmit

    @onsubmit.setter
    def onsubmit(self, callback):
        if self.onsubmit is not None:
            self._onsubmit = callback

    @property
    def user_interaction():
        return self._user_interaction

    async def on_submit(self, interaction, /):
        self._user_interaction = interaction
        await super().on_submit(interaction)
        if self.onsubmit is not None:
            await self.onsubmit(self, interaction)
        self.stop()

    async def on_timeout(self):
        if self.timeout_callback is not None:
            await self.timeout_callback(self)
        await super().on_timeout()

    async def wait(self):
        result = await super().wait()
        return result, self.user_interaction
