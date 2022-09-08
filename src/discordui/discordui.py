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
import asyncio

class View(discord.ui.View):
    def __init__(self, ctx, checkCallback=None):
        super().__init__()
        self.ctx = ctx
        self.checkCallback = None

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author and (self.checkCallback is None or self.checkCallback(self.ctx, self.interaction))

class Dropdown(discord.ui.Select):
    def __init__(self, ctx, placeholder=None, minval=1, maxval=1, *args, **kargs):
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
        result = await self.view.wait()
        return result

    async def callback(self, interaction):
        self.view.stop()

    @property
    def value(self):
        return self.values[0] if len(self.values) > 0 else None

class Button(discord.ui.Button):
    def __init__(self, style=discord.ButtonStyle.primary, label=None, custom_id=None, url=None, emoji=None):
        super().__init__(style=style, label=label, custom_id=custom_id, url=url, emoji=emoji)
        self.ctx = None
        self.group = None

    def _bindToGroup(self, ctx, grp):
        self.ctx = ctx
        self.group = grp

    @property
    def string_id(self):
        return str(self.custom_id)

    async def callback(self, interaction):
        if interaction.data.get("custom_id", None) == self.string_id:
            self.group.stop(self.custom_id)

class ButtonGroup(View):
    def __init__(self, ctx, *buttons):
        super().__init__(ctx)
        self.buttons = []
        self.value = None
        if len(buttons) > 0:
            self.addrange(*buttons)

    def __iadd__(self, button):
        self.addrange(button)
        return self

    def add(self, button):
        self.addrange(button)

    def addrange(self, *buttons):
        for b in buttons:
            b._bindToGroup(self.ctx, self)
            self.buttons.append(b)
            self.add_item(b)

    def stop(self, value):
        super().stop()
        self.value = value

    async def wait(self):
        try: interaction = await self.ctx.bot.wait_for('interaction', timeout=self.timeout, check=self.interaction_check)
        except asyncio.TimeoutError:
            await self.on_timeout()
            return True
        for child in self.children:
            await child.callback(interaction)
        await interaction.response.defer()
        return False
