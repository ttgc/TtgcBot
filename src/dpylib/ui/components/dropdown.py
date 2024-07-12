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
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Sequence, Type, override, final, TYPE_CHECKING
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


class BaseDropdown[T](ILocalizable[None], ABC):
    def __init__(
            self, *,
            on_select: Optional[AsyncCallable[Any]] = None,
            placeholder: Optional[str] = None,
    ) -> None:
        self.on_select = on_select
        self.placeholder = placeholder

    @property
    @abstractmethod
    def _values(self) -> list[T]:
        pass

    @property
    def value(self) -> Optional[T]:
        return self._values[0] if self._values else None

    @final
    async def callback(self, interaction: discord.Interaction) -> Any:
        if self.on_select:
            return await self.on_select(self, interaction)
        return None

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        if isinstance(self.placeholder, LocalizedStr):
            self.placeholder = await self.placeholder.localize(ctx, *args, **kwargs)


class Dropdown(BaseDropdown[str], ui.Select):
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
    ) -> None:
        BaseDropdown.__init__(self, on_select=on_select, placeholder=placeholder)
        ui.Select.__init__(
            self,
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
    @override
    def _values(self) -> list[str]:
        return self.values

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

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        await super().localize(ctx, *args, **kwargs)

        for opt in self.options:
            if isinstance(opt.label, LocalizedStr):
                opt.label = await opt.label.localize(ctx, *args, **kwargs)
            if isinstance(opt.description, LocalizedStr):
                opt.description = await opt.description.localize(ctx, *args, **kwargs)


class RoleDropdown(BaseDropdown[discord.Role], ui.RoleSelect):
    def __init__(
            self, *,
            default: Optional[discord.Role | list[discord.Role]] = None,
            on_select: Optional[AsyncCallable[Any]] = None,
            placeholder: Optional[str] = None,
            min_values: int = 1,
            max_values: int = 1,
            disabled: bool = False,
            custom_id: str = discord.utils.MISSING,
            row: Optional[int] = None
    ) -> None:
        BaseDropdown.__init__(self, on_select=on_select, placeholder=placeholder)
        ui.RoleSelect.__init__(
            self,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
            default_values=[default] if isinstance(default, discord.Role) else default if default else discord.utils.MISSING
        )
        self.on_select = on_select

    @property
    @override
    def _values(self) -> list[discord.Role]:
        return self.values


def dropdown[T: BaseDropdown, K](
        *, options: Optional[list[OptionType]] = None,
        default: Optional[K | list[K]] = None,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        custom_id: str = discord.utils.MISSING,
        row: Optional[int] = None,
        cls: Type[T] = Dropdown
) -> Callable[[AsyncCallable[Any]], Callable[..., T]]:
    def _decorator(func: AsyncCallable[Any]) -> Callable[..., cls]:
        if options and not issubclass(cls, Dropdown):
            raise TypeError(f'Invalid dropdown: {cls.__name__} cannot have custom options')

        kwargs = {
            'default': default,
            'min_values': min_values,
            'max_values': max_values,
            'disabled': disabled,
            'custom_id': custom_id,
            'row': row
        }

        if issubclass(cls, Dropdown):
            kwargs['options'] = options if options else []

        def _wrapper(*args, **kwargs) -> cls:
            return cls(
                on_select=functools.partial(func, *args, **kwargs),
                placeholder=placeholder,
                **kwargs
            )

        return _wrapper
    return _decorator
