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


from typing import Callable, Optional, Any
import functools
import time
from utils.aliases import AsyncCallable
from utils.decorators import unique


@unique(0)
class _Resource[T]:
    def __init__(self, name: str, *, ttl: int = 24) -> None:
        self.name = name
        self.ttl = ttl
        self.creation = 0
        self._value: Optional[T] = None

    @property
    def value(self) -> T:
        if not self.is_set:
            raise ValueError('Resource not initialized') # TODO: better exceptions
        if not self.alive:
            raise ValueError('TTL expired') # TODO: better exceptions
        return self._value # type: ignore

    @value.setter
    def value(self, value: T) -> None:
        self.value = value
        self.creation = time.time()

    @property
    def alive(self) -> bool:
        return self.ttl < 0 or time.time() - self.creation < self.ttl * 3600

    @property
    def is_set(self) -> bool:
        return self._value is not None

    def kill(self) -> None:
        self.creation = 0
        self._value = None


def pull_resource[T](name: str, *, ttl: int = 24, force: bool = False) -> Callable:
    def _decorator(fct: AsyncCallable[T]) -> AsyncCallable[T]:

        @functools.wraps(fct)
        async def _wrapper(*args, **kwargs) -> T:
            res = _Resource(name, ttl=ttl)

            if force:
                res.kill()
            if not res.is_set or not res.alive:
                res.value = await fct(*args, **kwargs)

            return res.value

        return _wrapper
    return _decorator


def invalidate_resource(name: str) -> Callable:
    def _decorator(fct: AsyncCallable[Any]) -> AsyncCallable[Any]:

        @functools.wraps(fct)
        async def _wrapper(*args, **kwargs):
            _Resource(name).kill()
            return await fct(*args, **kwargs)

        return _wrapper
    return _decorator
