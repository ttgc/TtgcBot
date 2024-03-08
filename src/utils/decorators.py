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


from typing import Type, Callable, Optional, Self, Any, final
import functools
from exceptions import DeprecatedException, AlreadyCalledFunctionException


def singleton(cls: Type) -> Callable:
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def unique(attr: int | str) -> Callable:
    def _decorator(cls: Type) -> Type:
        _instance = {}

        @final
        class _Wrapper(cls):
            def __new__(cls, *args, **kwargs) -> Self:
                if cls not in _instance:
                    _instance[cls] = {}

                to_fetch = args if isinstance(attr, int) else kwargs
                if (attr_value := to_fetch[attr]) not in _instance[cls]: # type: ignore
                    _instance[cls][attr_value] = object.__new__(cls)
                    _instance[cls][attr_value]._initialized = False

                return _instance[cls][attr_value]

            def __init__(self, *args, **kwargs) -> None:
                if not self._initialized:
                    super().__init__(*args, **kwargs)
                    self._initialized = True

        return _Wrapper
    return _decorator


def call_once(raise_error: bool = False) -> Callable:
    def call_once_decorator(fct: Callable) -> Callable:
        called = {}

        @functools.wraps(fct)
        def call_fct(*args, **kwargs) -> Any:
            if fct not in called:
                called[fct] = fct(*args, **kwargs)
            elif raise_error:
                raise AlreadyCalledFunctionException(fct)
            return called[fct]

        return call_fct
    return call_once_decorator


def deprecated(reason: str, *, raise_error: bool = True, logger: Optional[Callable[..., None]] = None) -> Callable:
    def deprecated_decorator(fct: Callable | Type) -> Callable:
        log_method = logger if logger else print
        log_method(f"Deprecated function/class: {fct.__name__}\nReason: {reason}")

        @functools.wraps(fct)
        def deprecated_call(*args, **kwargs) -> Any:
            exception = DeprecatedException(fct, reason, *args, **kwargs)

            if raise_error:
                raise exception

            log_method(str(exception))
            return fct(*args, **kwargs)

        return deprecated_call
    return deprecated_decorator
