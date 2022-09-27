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

class Dropdown(discord.ui.Select):
    def __init__(self, ctx, view, *, id=None, placeholder=None, minval=1, maxval=1, disabled=False, row=None, onselection=None, options=[], **kargs):
        self.ctx = ctx
        opt = [discord.SelectOption(label=i) for i in options]
        opt += [discord.SelectOption(label=i, value=k) for i, k in kargs.items()]
        if id is not None:
            super().__init__(custom_id=id, placeholder=placeholder, min_values=minval, max_values=maxval, options=opt, disabled=disabled, row=row)
        else:
            super().__init__(placeholder=placeholder, min_values=minval, max_values=maxval, options=opt, disabled=disabled, row=row)
        view.add_item(self)
        self._view = view
        self._onselection = onselection

    def __iadd__(self, item):
        if isinstance(item, discord.ui.SelectOption):
            self.append_option(item)
        else:
            self.add_option(label=str(item))

    @property
    def view(self):
        return self._view

    @property
    def value(self):
        return self.values[0] if len(self.values) > 0 else None

    @property
    def onselection(self):
        return self._onselection

    @onselection.setter
    def onselection(self, value):
        self._onselection = value

    async def callback(self, interaction):
        if self.onselection is not None:
            await self.onselection(self, interaction)
        else:
            await interaction.response.defer()

    def add_multiple_options(self, *args, **kwargs):
        for i in args:
            self += i
        for i, k in kwargs.items():
            self.add_option(label=i, value=k)


class StandaloneDropdown(Dropdown):
    def __init__(self, ctx, *, id=None, placeholder=None, minval=1, maxval=1, disabled=False, row=None, onselection=None, check_callback=None, timeout=None, options=[], **kargs):
        view = View(ctx, check_callback=check_callback, timeout=timeout)
        super().__init__(ctx, view, id=id, placeholder=placeholder, minval=minval, maxval=maxval, disabled=disabled, row=row, onselection=onselection, options=options, **kargs)

    async def wait(self):
        result = await self.view.wait()
        return result

    async def callback(self, interaction):
        await super().callback(interaction)
        self.view.stop()
