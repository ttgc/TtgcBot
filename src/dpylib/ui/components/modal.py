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


from typing import Self, Optional, Callable, Awaitable, Any, override, TYPE_CHECKING
from discord import ui
import discord
from utils.decorators import forbidden
from utils.aliases import AsyncCallable
from config import Log
from lang import LocalizedStr
from .view import View

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


class Modal(View, ui.Modal):
    @override
    def __init__(
            self,
            title: str,
            on_submit: AsyncCallable[None], *,
            timeout: Optional[float] = None,
            custom_id: str = discord.utils.MISSING,
            **kwargs
    ) -> None:
        ui.Modal.__init__(self, timeout=timeout, title=title, custom_id=custom_id)
        View.__init__(self, **kwargs)
        self._on_submit = on_submit

    @forbidden(logger=Log.error)
    async def send(self, ctx: 'ExtendedContext') -> None:
        pass

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        await View.localize(self, ctx, *args, **kwargs)

        if isinstance(self.title, LocalizedStr):
            self.title = await self.title.localize(ctx, *args, **kwargs)

    @override
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.stop()
        await self._on_submit(self, interaction)


def modal(title: str, *,
        timeout: Optional[float] = None,
        custom_id: str = discord.utils.MISSING
) -> Callable[[AsyncCallable[None]], Modal]:
    def _decorator(func: AsyncCallable[None]) -> Modal:
        return Modal(
            title,
            func,
            timeout=timeout,
            custom_id=custom_id
        )
    return _decorator
