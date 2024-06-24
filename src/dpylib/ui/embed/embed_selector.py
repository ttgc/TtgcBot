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


import discord
from typing import Optional, Callable, Awaitable, override
from utils.aliases import UserType
from utils.emojis import Emoji
from ...common.embed import DiscordEmbedMeta
from ..components import dropdown, button, Dropdown, DropdownOption, Button
from .embed_browser import EmbedBrowserView


class EmbedBrowserSelectorView(EmbedBrowserView):
    def __init__(
            self,
            embed: DiscordEmbedMeta,
            on_validate: Callable[[str, discord.Interaction], Awaitable[None]], *,
            on_reject: Optional[Callable[[discord.Interaction], Awaitable[None]]] = None,
            timeout: Optional[float] = None,
            owner: Optional[UserType] = None
    ) -> None:
        super().__init__(embed, timeout=timeout, owner=owner)
        self.selector = self._selector()
        self.on_validate = on_validate
        self.on_reject = on_reject
        self += self.selector

    @override
    def _build_page(self) -> DiscordEmbedMeta:
        page = super()._build_page()
        self.remove_item(self.selector)
        self.selector = self._selector()
        self.selector += [DropdownOption(x.name, x.name, x.content) for x in page.fields]
        self += self.selector
        return page

    @dropdown(options=[], placeholder='', row=2)
    async def _selector(self, dd: Dropdown, interaction: discord.Interaction) -> None:
        await self.on_validate(dd.value if dd.value else '', interaction)
        self.stop()

    @button(style=discord.ButtonStyle.secondary, row=1, emoji=Emoji.X)
    @override
    async def _terminate(self, btn: Button, interaction: discord.Interaction) -> None:
        if self.on_reject:
            await self.on_reject(interaction)
        else:
            await interaction.response.edit_message(view=None)

        self.stop()
