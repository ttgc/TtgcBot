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
from discordui.views import DefaultViewResults, ViewResult
from utils.emojis import Emoji
from enum import Enum

class Button(discord.ui.Button):
    def __init__(self, ctx, view, *, style=discord.ButtonStyle.primary, label=None, id=None, url=None, emoji=None, disabled=False, row=None, onclick=None, final=False, finalize_check=None, view_result=DefaultViewResults.DEFAULT):
        super().__init__(style=style, label=label, custom_id=id, url=url, emoji=emoji, disabled=disabled, row=row)
        self.ctx = ctx
        self._onclick = onclick
        view.add_item(self)
        self._view = view
        self._final = final
        self._finalize_check = finalize_check
        self._view_result = view_result

    @property
    def view(self):
        return self._view

    @property
    def onclick(self):
        return self._onclick

    @onclick.setter
    def onclick(self, value):
        self._onclick = value

    @property
    def final(self):
        return self._final

    @final.setter
    def final(self, value):
        self._final = value

    @property
    def finalize_check(self):
        return self._finalize_check

    @finalize_check.setter
    def finalize_check(self, value):
        self._finalize_check = value

    @property
    def view_result(self):
        return self._view_result

    @view_result.setter
    def view_result(self, value):
        self._view_result = value

    async def callback(self, interaction):
        if self.finalize_check is not None:
            self.final = self.finalize_check(self, interaction)

        if self.onclick is not None:
            await self.onclick(self, interaction)
        else:
            await interaction.response.defer()

        if self.final:
            self.view.result = self.view_result
            self.view.stop()


class DefaultButtons(Enum):
    CANCEL = {
        "style": discord.ButtonStyle.secondary,
        "label": "Cancel",
        "emoji": str(Emoji.X),
        "final": True,
        "view_result": DefaultViewResults.CANCEL
    }

    SUBMIT = {
        "style": discord.ButtonStyle.success,
        "label": "Submit",
        "emoji": str(Emoji.WHITE_CHECK_MARK),
        "final": True,
        "view_result": DefaultViewResults.SUBMIT
    }

    ADD = {
        "style": discord.ButtonStyle.success,
        "emoji": str(Emoji.PLUS),
        "view_result": ViewResult(1)
    }

    REMOVE = {
        "style": discord.ButtonStyle.danger,
        "emoji": str(Emoji.MINUS),
        "view_result": ViewResult(-1, is_success=True)
    }

    SET = {
        "emoji": str(Emoji.EQUAL),
        "view_result": ViewResult(0, is_success=True)
    }

    def spawn(self, view, **overrides):
        keys = dict(self.value)
        for i, k in overrides.items():
            keys[i] = k

        return Button(view.ctx, view, **keys)
