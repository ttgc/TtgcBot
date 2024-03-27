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


from typing import Any, Optional, Callable, override
import discord
from discord import ui
from utils.aliases import AsyncCallable


class Button(ui.Button):
    def __init__(
            self, *,
            on_click: AsyncCallable[Any],
            style: discord.ButtonStyle = discord.ButtonStyle.secondary,
            label: Optional[str] = None,
            disabled: bool = False,
            custom_id: Optional[str] = None,
            url: Optional[str] = None,
            emoji: Optional[str | discord.Emoji | discord.PartialEmoji] = None,
            row: Optional[int] = None
    ):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.on_click = on_click

    @override
    async def callback(self, interaction: discord.Interaction) -> Any:
        return await self.on_click(self, interaction)


def button(
        *, style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[str | discord.Emoji | discord.PartialEmoji] = None,
        row: Optional[int] = None
) -> Callable[[AsyncCallable[Any]], Button]:
    def _decorator(func:AsyncCallable[Any]) -> Button:
        return Button(
            on_click=func,
            label=label,
            style=style,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row
        )
    return _decorator
