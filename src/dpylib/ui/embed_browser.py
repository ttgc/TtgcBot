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


from typing import Optional, override, TYPE_CHECKING
import discord
from utils.aliases import UserType
from .components import View, Button, button
from ..common.embed import DiscordEmbedMeta, EmbedConversionPolicy, EmbedLimits, EmbedIconTexttMeta

if TYPE_CHECKING:
    from ..common.contextext import ExtendedContext


class EmbedBrowserView(View):
    def __init__(self, embed: DiscordEmbedMeta, *, timeout: Optional[float] = None, owner: Optional[UserType]) -> None:
        super().__init__(timeout=timeout, owner=owner)
        self.embed = embed
        self.page_count = len(self.embed.fields) // EmbedLimits.FIELDS_COUNT
        self.cur_page = 0

    def _build_page(self) -> DiscordEmbedMeta:
        page_str = f'Page {self.cur_page + 1} / {self.page_count + 1}'
        footer = self.embed.footer
        pmin = self.cur_page * EmbedLimits.FIELDS_COUNT
        pmax = (self.cur_page + 1) * EmbedLimits.FIELDS_COUNT

        if not footer:
            footer = page_str
        if isinstance(footer, EmbedIconTexttMeta):
            footer.text = f'{footer.text}\n{page_str}'
        else:
            footer = f'{footer}\n{page_str}'

        return DiscordEmbedMeta(
            title=self.embed.title,
            color=self.embed.color,
            descr=self.embed.descr,
            link=self.embed.link,
            thumbnail=self.embed.thumbnail,
            author=self.embed.author,
            footer=footer,
            fields=self.embed.fields[pmin:pmax]
        )

    @override
    async def send(self, ctx: 'ExtendedContext') -> None:
        self._reset_buttons()
        await ctx.send(view=self, reference=ctx.message, embed=self._build_page().convert(policy=EmbedConversionPolicy.TRUNCATE))

    def _reset_buttons(self) -> None:
        self.first.disabled = self.cur_page <= 0
        self.previous.disabled = self.cur_page <= 0
        self.next.disabled = self.cur_page >= self.page_count
        self.last.disabled = self.cur_page >= self.page_count

    @button(style=discord.ButtonStyle.primary, row=0, emoji='', disabled=True)
    async def first(self, btn: Button, interaction: discord.Interaction) -> None:
        self.cur_page = 0
        self._reset_buttons()
        await interaction.response.edit_message(view=self, embed=self._build_page().convert(policy=EmbedConversionPolicy.TRUNCATE))

    @button(style=discord.ButtonStyle.primary, row=0, emoji='', disabled=True)
    async def previous(self, btn: Button, interaction: discord.Interaction) -> None:
        self.cur_page -= 1
        self._reset_buttons()
        await interaction.response.edit_message(view=self, embed=self._build_page().convert(policy=EmbedConversionPolicy.TRUNCATE))

    @button(style=discord.ButtonStyle.primary, row=0, emoji='')
    async def next(self, btn: Button, interaction: discord.Interaction) -> None:
        self.cur_page += 1
        self._reset_buttons()
        await interaction.response.edit_message(view=self, embed=self._build_page().convert(policy=EmbedConversionPolicy.TRUNCATE))

    @button(style=discord.ButtonStyle.primary, row=0, emoji='')
    async def last(self, btn: Button, interaction: discord.Interaction) -> None:
        self.cur_page = self.page_count
        self._reset_buttons()
        await interaction.response.edit_message(view=self, embed=self._build_page().convert(policy=EmbedConversionPolicy.TRUNCATE))

    @button(style=discord.ButtonStyle.danger, row=0, emoji='x')
    async def terminate(self, btn: Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=None)
        self.stop()
