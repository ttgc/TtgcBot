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


from typing import Optional, Callable, Self, Awaitable, TYPE_CHECKING, override
import discord
from discord import ui
from dpylib.common.contextext import ExtendedContext
from utils.decorators import convert_none_to_list
from utils.aliases import UserType
from ..common.embed import DiscordEmbedMeta
from .components import View

if TYPE_CHECKING:
    from ..common.contextext import ExtendedContext


class EmbedView(View):
    @convert_none_to_list('checks')
    @override
    def __init__(
            self, *,
            embed: DiscordEmbedMeta,
            timeout: Optional[float] = None,
            owner: Optional[UserType] = None,
            checks: list[Callable[[Self, discord.Interaction], bool]] = None, # type: ignore
            on_timeout: Optional[Callable[[Self], Awaitable[None]]] = None,
            on_error: Optional[Callable[[Self, discord.Interaction, Exception, ui.Item], Awaitable[None]]] = None
    ) -> None:
        super().__init__(timeout=timeout, owner=owner, checks=checks, on_timeout=on_timeout, on_error=on_error)
        self.embed = embed

    @override
    async def send(self, ctx: 'ExtendedContext', *, content: Optional[str] = None, **kwargs) -> None:
        await super().send(ctx, content=content, embed=self.embed.convert(), **kwargs)

    @override
    async def localize(self, ctx: ExtendedContext, *args, **kwargs) -> None:
        await super().localize(ctx, *args, **kwargs)
        await self.embed.localize(ctx, *args, **kwargs)
