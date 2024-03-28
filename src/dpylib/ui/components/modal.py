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


import functools
from typing import Optional, Self, Awaitable, Callable, override, TYPE_CHECKING
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
            custom_id: str = discord.utils.MISSING,
            on_error: Optional[Callable[[Self, discord.Interaction, Exception], Awaitable[None]]] = None,
            **kwargs
    ) -> None:
        ui.Modal.__init__(self, timeout=None, title=title, custom_id=custom_id)
        View.__init__(self, timeout=None, **kwargs)
        self._on_submit = on_submit
        self._on_error = on_error

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

    @override
    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception) -> None:
        if self._on_error:
            await self._on_error(self, interaction, error)
        else:
            await ui.Modal.on_error(self, interaction, error)


def modal(title: str, *, custom_id: str = discord.utils.MISSING) -> Callable[[AsyncCallable[None]], Callable[..., Modal]]:
    def _decorator(func: AsyncCallable[None]) -> Callable[..., Modal]:
        def _wrapper(*args, **kwargs) -> Modal:
            return Modal(
                title,
                functools.partial(func, *args, **kwargs),
                custom_id=custom_id
            )
        return _wrapper
    return _decorator
