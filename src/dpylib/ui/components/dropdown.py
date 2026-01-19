#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2026  Thomas PIOT
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
from dataclasses import dataclass
from typing import Any, Optional, Callable, Sequence, override, TYPE_CHECKING
import discord
from discord import ui
from utils.aliases import AsyncCallable
from utils.emojis import Emoji
from lang import ILocalizable, LocalizedStr

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


@dataclass
class DropdownOption:
    name: str
    value: str
    description: Optional[str] = None
    emoji: Optional[Emoji] = None

    def __str__(self) -> str:
        return self.name


type OptionType = str | DropdownOption


class Dropdown(ui.Select, ILocalizable[None]):
    def __init__(
            self, *,
            options: list[OptionType],
            default: Optional[str | list[str]] = None,
            on_select: Optional[AsyncCallable[Any]] = None,
            placeholder: Optional[str] = None,
            min_values: int = 1,
            max_values: int = 1,
            disabled: bool = False,
            custom_id: str = discord.utils.MISSING,
            row: Optional[int] = None
    ):
        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row
        )
        self.on_select = on_select
        self += options

        if default:
            self.default = default

    def __iadd__(self, option: OptionType | Sequence[OptionType]):
        if isinstance(option, str):
            self.add_option(label=option, value=option)
        elif isinstance(option, DropdownOption):
            emoji = str(option.emoji) if option.emoji else None
            self.add_option(label=option.name, value=option.value, description=option.description, emoji=emoji)
        else:
            for opt in option:
                self += opt

        return self

    @property
    def default(self) -> list[str] | str:
        items = [x.value for x in self.options if x.default]
        return items if len(items) != 1 else items[0]

    @default.setter
    def default(self, value: list[str] | str) -> None:
        for opt in self.options:
            is_strdefault = isinstance(value, str) and opt.value == value
            is_lsdefault = isinstance(value, list) and opt.value in value
            opt.default = is_strdefault or is_lsdefault

    @default.deleter
    def default(self) -> None:
        for opt in self.options:
            opt.default = False

    @property
    def value(self) -> Optional[str]:
        return self.values[0] if self.values else None

    @override
    async def callback(self, interaction: discord.Interaction) -> Any:
        if self.on_select:
            return await self.on_select(self, interaction)
        return None

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        if isinstance(self.placeholder, LocalizedStr):
            self.placeholder = await self.placeholder.localize(ctx, *args, **kwargs)

        for opt in self.options:
            if isinstance(opt.label, LocalizedStr):
                opt.label = await opt.label.localize(ctx, *args, **kwargs)
            if isinstance(opt.description, LocalizedStr):
                opt.description = await opt.description.localize(ctx, *args, **kwargs)


def dropdown(
        *, options: list[OptionType],
        default: Optional[str | list[str]] = None,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        custom_id: str = discord.utils.MISSING,
        row: Optional[int] = None
) -> Callable[[AsyncCallable[Any]], Callable[..., Dropdown]]:
    def _decorator(func: AsyncCallable[Any]) -> Callable[..., Dropdown]:
        def _wrapper(*args, **kwargs) -> Dropdown:
            return Dropdown(
                options=options,
                default=default,
                on_select=functools.partial(func, *args, **kwargs),
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                disabled=disabled,
                custom_id=custom_id,
                row=row
            )
        return _wrapper
    return _decorator
