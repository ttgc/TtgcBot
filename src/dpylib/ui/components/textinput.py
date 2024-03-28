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


from typing import Type, Callable, Optional, override, TYPE_CHECKING
import discord
from discord import ui
from lang import ILocalizable, LocalizedStr
from utils.decorators import catch
from config import Log

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


class TextInput[T](ui.TextInput, ILocalizable[None]):
    def __init__(
            self,
            label: str, *,
            paragraph: bool = False,
            custom_id: str = discord.utils.MISSING,
            placeholder: Optional[str] = None,
            default: Optional[str] = None,
            required: bool = False,
            min_length: Optional[int] = None,
            max_length: Optional[int] = None,
            row: Optional[int] = None,
            cast: Type[T] | Callable[[str], T] = str
    ):
        style = discord.TextStyle.paragraph if paragraph else discord.TextStyle.short
        super().__init__(
            label=label,
            style=style,
            custom_id=custom_id,
            placeholder=placeholder,
            default=default,
            required=required,
            min_length=min_length,
            max_length=max_length,
            row=row
        )
        self.cast = cast

    @property
    @catch(Exception, error_value=None, logger=Log.debug)
    @override
    def value(self) -> Optional[T]:
        return self.cast(super().value)

    @property
    def raw_value(self) -> str:
        return super().value

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        if isinstance(self.label, LocalizedStr):
            self.label = await self.label.localize(ctx, *args, **kwargs)
        if isinstance(self.placeholder, LocalizedStr):
            self.placeholder = await self.placeholder.localize(ctx, *args, **kwargs)
