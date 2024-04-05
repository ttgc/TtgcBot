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
from typing import TYPE_CHECKING, Callable, override, final
from enum import StrEnum
from abc import ABC, abstractmethod
from lang import ILocalizable
from ..ui.components import View

if TYPE_CHECKING:
    from ..common.contextext import ExtendedContext


class IWorkflow[T](ILocalizable[None], ABC):
    class ViewID(StrEnum):
        pass

    def __init__(self) -> None:
        self.views: dict[str, View] = {}
        self._started = False

    def __getitem__(self, key: str) -> View:
        return self.views[key]

    @final
    async def __call__(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        if self._started:
            raise Exception('TEMP') # TODO: proper exception

        self._started = True
        await self.localize(ctx, *args, **kwargs)
        await self.start(ctx)

    @abstractmethod
    async def start(self, ctx: 'ExtendedContext') -> None:
        pass

    @abstractmethod
    async def finalize(self) -> T:
        pass

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for view in self.views.values():
            await view.localize(ctx, *args, **kwargs)


def setup_view(name: str) -> Callable[[Callable[..., View]], Callable[..., View]]:
    def _decorator(func: Callable[..., View]) -> Callable[..., View]:

        @functools.wraps(func)
        def _wrapper(self: IWorkflow, *args, **kwargs):
            view = func(self, *args, **kwargs)
            self.views[name] = view
            return view

        return _wrapper
    return _decorator
