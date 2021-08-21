#!usr/bin/env python3.7
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

class View(discord.ui.View):
    def __init__(self, ctx, checkCallback=None):
        super().__init__()
        self.ctx = ctx
        self.checkCallback = None

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author and (self.checkCallback is None or self.checkCallback(self.ctx, self.interaction))

class Dropdown(discord.ui.Select):
    def __init__(self, bot, ctx, placeholder=None, minval=1, maxval=1, *args, **kargs):
        self.bot = bot
        self.ctx = ctx
        options = [discord.SelectOption(label=i) for i in args]
        options += [discord.SelectOption(label=i, value=k) for i, k in kargs.items()]
        super().__init__(placeholder=placeholder, min_values=minval, max_values=maxval, options=options)
        self._view = View(self.ctx)
        self._view.add_item(self)

    @property
    def view(self):
        return self._view

    async def wait(self):
        print("waiting...")
        result = await self.view.wait()
        print(result)
        return result

    async def callback(self, interaction):
        self.view.stop()

    @property
    def value(self):
        return self.values[0] if len(self.values) > 0 else None
