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
from typing import Self, Optional, Callable, override, TYPE_CHECKING
from dataclasses import dataclass
from enum import StrEnum
import discord
from discord import ui
from utils.aliases import AsyncCallable
from lang import ILocalizable, LocalizedStr

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


class BoxItemValue(StrEnum):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.flag_value = 0b1 << len(self.__class__)

    def __int__(self) -> int:
        return self.flag_value

    def cast[T](self, converter: Callable[[str], T]) -> T:
        return converter(self.value)

    @classmethod
    def from_str_or_default(cls, value: str, *, default: Optional[Self] = None) -> Optional[Self]:
        for x in cls:
            if x == value:
                return x
        return default

    @classmethod
    def from_str(cls, value: str, *, default: Optional[Self] = None) -> Self:
        if (converted := cls.from_str_or_default(value, default=default)) is None:
            raise ValueError(f'Value {value} does not match any {cls.__name__} value')
        return converted


@dataclass(frozen=True, kw_only=True)
class BoxItem:
    label: str
    value: BoxItemValue
    description: Optional[str] = None
    selected_by_default: bool = False

    @property
    def as_checkbox_option(self) -> discord.CheckboxGroupOption:
        return discord.CheckboxGroupOption(
            label=self.label,
            value=str(self.value),
            description=self.description,
            default=self.selected_by_default
        )

    @property
    def as_radiobox_option(self) -> discord.RadioGroupOption:
        return discord.RadioGroupOption(
            label=self.label,
            value=str(self.value),
            description=self.description,
            default=self.selected_by_default
        )


class CheckboxGroup(ui.CheckboxGroup, ILocalizable[None]):
    def __init__(
            self, *,
            custom_id: Optional[str] = None,
            required: bool = True,
            min_values: Optional[int] = None,
            max_values: Optional[int] = None,
            options: Optional[list[discord.CheckboxGroupOption]] = None,
            id: Optional[int] = None
    ) -> None:
        super().__init__(
            custom_id=custom_id,
            required=required,
            min_values=min_values,
            max_values=max_values,
            options=options if options else [],
            id=id
        )

    def __iadd__(self, option: BoxItem) -> Self:
        self.append_option(option.as_checkbox_option)
        return self

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for opt in self.options:
            if isinstance(opt.label, LocalizedStr):
                opt.label = await opt.label.localize(ctx, *args, **kwargs)
            if isinstance(opt.description, LocalizedStr):
                opt.description = await opt.description.localize(ctx, *args, **kwargs)

    @property
    def values(self) -> list[BoxItemValue]:
        return [BoxItemValue.from_str(x) for x in super().values]

    def cast_values[T](self, converter: Callable[[str], T]) -> list[T]:
        return [x.cast(converter) for x in self.values]

    @property
    def bitmask(self) -> int:
        value = 0b0
        for x in self.values:
            value |= int(x)
        return value


class RadioGroup(ui.RadioGroup, ILocalizable[None]):
    def __init__(
            self, *,
            custom_id: Optional[str] = None,
            required: bool = True,
            options: Optional[list[discord.RadioGroupOption]] = None,
            id: Optional[int] = None
    ) -> None:
        super().__init__(
            custom_id=custom_id,
            required=required,
            options=options,
            id=id
        )

    def __iadd__(self, option: BoxItem) -> Self:
        self.append_option(option.as_radiobox_option)
        return self

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for opt in self.options:
            if isinstance(opt.label, LocalizedStr):
                opt.label = await opt.label.localize(ctx, *args, **kwargs)
            if isinstance(opt.description, LocalizedStr):
                opt.description = await opt.description.localize(ctx, *args, **kwargs)

    @property
    def value(self) -> BoxItemValue:
        return BoxItemValue.from_str(super().value)

    def cast_values[T](self, converter: Callable[[str], T]) -> list[T]:
        return self.value.cast(converter)
