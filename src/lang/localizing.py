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


from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, override, Optional

if TYPE_CHECKING:
    from dpylib.common.contextext import ExtendedContext


async def localize(ctx: 'ExtendedContext', msgkey: str, *args, **kwargs) -> str:
    lang = await ctx.ext.get_lang()
    return lang[msgkey].format(*args, **kwargs)


class ILocalizable[T](ABC):
    @abstractmethod
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> T:
        pass


class LocalizedStr(str, ILocalizable[str]):
    def __init__(self, _: str, *, argc: int = -1, kwargs_inuse: Optional[list[str]] = None) -> None:
        super().__init__()
        self.argc = argc
        self.kwargs_inuse = kwargs_inuse

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> str:
        if self.argc >= 0 and len(args) > self.argc:
            args = list(args)[:self.argc]

        if self.kwargs_inuse is not None:
            saved = {}

            for key in self.kwargs_inuse:
                saved[key] = kwargs[key]

            kwargs = saved

        return await localize(ctx, str(self), *args, **kwargs)
