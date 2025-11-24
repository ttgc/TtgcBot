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


import asyncio
from typing import Self, Optional, Callable, Awaitable, Type, override, TYPE_CHECKING
from discord import ui
import discord
from utils.aliases import UserType
from utils.decorators import convert_none_to_list, deprecated
from config import Log
from lang import ILocalizable

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


class View(ui.View, ILocalizable[None]):
    @convert_none_to_list('checks')
    @override
    def __init__(
            self, *,
            timeout: Optional[float] = None,
            owner: Optional[UserType] = None,
            checks: list[Callable[[Self, discord.Interaction], bool]] = None, # type: ignore
            on_timeout: Optional[Callable[[Self], Awaitable[None]]] = None,
            on_error: Optional[Callable[[Self, discord.Interaction, Exception, ui.Item], Awaitable[None]]] = None
    ) -> None:
        super().__init__(timeout=timeout)
        self.owner = owner
        self.checks = checks
        self._on_timeout = on_timeout
        self._on_error = on_error
        self.disable_on_stop = True

    @deprecated('Wait on views is not recommended', raise_error=False, logger=Log.debug_v4)
    @override
    async def wait(self) -> bool:
        return await super().wait()

    def __iadd__(self, item: ui.Item) -> Self:
        return self.add_item(item)

    @override
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.owner and interaction.user != self.owner:
            await interaction.response.defer()
            return False

        for chk in self.checks:
            if asyncio.iscoroutinefunction(chk):
                if not await chk(self, interaction):
                    await interaction.response.defer()
                    return False
            else:
                if not chk(self, interaction):
                    await interaction.response.defer()
                    return False

        return True

    @override
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: ui.Item) -> None:
        if self._on_error:
            await self._on_error(self, interaction, error, item)
        else:
            await super().on_error(interaction, error, item)

    @override
    def stop(self) -> None:
        for child in self.children:
            if self.disable_on_stop and hasattr(child, 'disabled'):
                setattr(child, 'disabled', True)

        super().stop()

    @override
    async def on_timeout(self) -> None:
        self.stop()

        if self._on_timeout:
            await self._on_timeout(self)

    async def send(self, ctx: 'ExtendedContext', *, content: Optional[str] = None, **kwargs) -> discord.Message:
        return await ctx.send(content, view=self, reference=ctx.message, **kwargs)

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for widget in self.children:
            if isinstance(widget, ILocalizable):
                await widget.localize(ctx, *args, **kwargs)

    def search[T](self, custom_id: str, return_type: Type[T] = ui.Item) -> Optional[T]:
        for child in self.children:
            if isinstance(child, return_type) and hasattr(child, 'custom_id') and getattr(child, 'custom_id') == custom_id:
                return child
        return None

    def find[T](self, custom_id: str, return_type: Type[T] = ui.Item) -> T:
        found = self.search(custom_id, return_type)

        if not found:
            raise ValueError(f'Custom ID {custom_id} does not exist in this view or is not of type {return_type.__name__}')

        return found

    def get_first_child[T](self, return_type: Type[T] = ui.Item) -> T:
        for child in self.children:
            if isinstance(child, return_type):
                return child
        raise ValueError(f'No child is matching return type {return_type.__name__}')


class LayoutView(ui.LayoutView, ILocalizable[None]):
    @convert_none_to_list('checks')
    @override
    def __init__(
            self, *,
            timeout: Optional[float] = None,
            owner: Optional[UserType] = None,
            checks: list[Callable[[Self, discord.Interaction], bool]] = None, # type: ignore
            on_timeout: Optional[Callable[[Self], Awaitable[None]]] = None,
            on_error: Optional[Callable[[Self, discord.Interaction, Exception, ui.Item], Awaitable[None]]] = None
    ) -> None:
        super().__init__(timeout=timeout)
        self.owner = owner
        self.checks = checks
        self._on_timeout = on_timeout
        self._on_error = on_error
        self.disable_on_stop = True

    @deprecated('Wait on views is not recommended', raise_error=False, logger=Log.debug_v4)
    @override
    async def wait(self) -> bool:
        return await super().wait()

    def __iadd__(self, item: ui.Item) -> Self:
        return self.add_item(item)

    @override
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.owner and interaction.user != self.owner:
            await interaction.response.defer()
            return False

        for chk in self.checks:
            if asyncio.iscoroutinefunction(chk):
                if not await chk(self, interaction):
                    await interaction.response.defer()
                    return False
            else:
                if not chk(self, interaction):
                    await interaction.response.defer()
                    return False

        return True

    @override
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: ui.Item) -> None:
        if self._on_error:
            await self._on_error(self, interaction, error, item)
        else:
            await super().on_error(interaction, error, item)

    @override
    def stop(self) -> None:
        for child in self.children:
            if self.disable_on_stop and hasattr(child, 'disabled'):
                setattr(child, 'disabled', True)

        super().stop()

    @override
    async def on_timeout(self) -> None:
        self.stop()

        if self._on_timeout:
            await self._on_timeout(self)

    async def send(self, ctx: 'ExtendedContext', **kwargs) -> None:
        await ctx.send(view=self, reference=ctx.message, **kwargs)

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for widget in self.children:
            if isinstance(widget, ILocalizable):
                await widget.localize(ctx, *args, **kwargs)

    def search[T](self, custom_id: str, return_type: Type[T] = ui.Item) -> Optional[T]:
        for child in self.children:
            if isinstance(child, return_type) and hasattr(child, 'custom_id') and getattr(child, 'custom_id') == custom_id:
                return child
        return None

    def find[T](self, custom_id: str, return_type: Type[T] = ui.Item) -> T:
        found = self.search(custom_id, return_type)

        if not found:
            raise ValueError(f'Custom ID {custom_id} does not exist in this view or is not of type {return_type.__name__}')

        return found

    def get_first_child[T](self, return_type: Type[T] = ui.Item) -> T:
        for child in self.children:
            if isinstance(child, return_type):
                return child
        raise ValueError(f'No child is matching return type {return_type.__name__}')
