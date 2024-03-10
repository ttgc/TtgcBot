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


from typing import Self
import time
import pytest
from utils import get_color, try_parse_int
from utils.emojis import Emoji
from utils.decorators import deprecated, call_once, singleton, unique
from exceptions import DeprecatedException, AlreadyCalledFunctionException


class TestUtils:
    def test_emoji(self) -> None:
        for emoji in Emoji:
            assert Emoji.from_str(f':{emoji.name.lower()}:') == emoji
        with pytest.raises(ValueError):
            Emoji.from_str('random failing test')

    def test_deprecated(self) -> None:
        @deprecated('testing purpose', raise_error=True)
        def _deprecated_raise() -> None:
            pass

        @deprecated('testing purpose', raise_error=False)
        def _deprecated() -> bool:
            return True

        with pytest.raises(DeprecatedException):
            _deprecated_raise()

        assert _deprecated()

    def test_call_once(self) -> None:
        @call_once(True)
        def _call_once_raise() -> None:
            pass

        @call_once(False)
        def _call_once() -> float:
            return time.time()

        _call_once_raise()
        with pytest.raises(AlreadyCalledFunctionException):
            _call_once_raise()

        ts = _call_once()
        time.sleep(1)
        assert ts == _call_once()

    def test_singleton(self) -> None:
        @singleton
        class _Singleton:
            def __init__(self, param: int) -> None:
                self.param = param

            def __eq__(self, __value: Self) -> bool:
                return self.param == __value.param

        assert _Singleton(0).param == 0
        assert _Singleton(1).param == 0
        assert _Singleton(0) == _Singleton(1)

    def test_unique(self) -> None:
        @unique(0)
        class _Unique:
            def __init__(self, param: int, param2: int) -> None:
                self.param = param
                self.param2 = param2

            def __eq__(self, __value: Self) -> bool:
                return self.param == __value.param

        assert _Unique(0, 1).param == 0
        assert _Unique(0, 1).param2 == 1
        assert _Unique(0, 1) == _Unique(0, 0)
        assert _Unique(1, 0) != _Unique(0, 1)
        assert _Unique(1, 0) == _Unique(1, 1)
        assert _Unique(0, 0).param2 == 1
        assert _Unique(1, 0).param2 == 0
        assert _Unique(1, 1).param2 == 0
        assert _Unique(1, 0).param == 1

    def test_try_parse_int(self) -> None:
        assert try_parse_int('1', 0) == 1
        assert try_parse_int('-1', 0) == -1
        assert try_parse_int('one', 0) == 0

    def test_get_color(self) -> None:
        r, g, b = get_color('FF882A').to_rgb()
        assert r == 255
        assert g == 0x88
        assert b == 0x2A
