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


from typing import Self, Callable
from random import randint, choice
from enum import Enum
import re


def _parenthesis_handle(match: re.Match):
    return Expression(match[1])()


def _dice_generate(match: re.Match) -> str:
    amount, sides = match.groups()
    results = [randint(1, int(sides)) for _ in range(int(amount))]
    return str(sum(results))


def _dice_spe_generate(match: re.Match) -> str:
    amount, content = match.groups()
    possibilities = [x.strip() for x in content.split(',')]
    results = [choice(possibilities) for _ in range(int(amount))]
    return ', '.join(results)


def _mul_handle(match: re.Match) -> str:
    fact1, fact2 = match.groups()
    return str(float(fact1) * float(fact2))


def _div_handle(match: re.Match) -> str:
    fact1, fact2 = match.groups()
    return str(float(fact1) / float(fact2))


def _divent_handle(match: re.Match) -> str:
    fact1, fact2 = match.groups()
    return str(int(fact1) // int(fact2))


def _mod_handle(match: re.Match) -> str:
    fact1, fact2 = match.groups()
    return str(int(fact1) % int(fact2))


def _add_handle(match: re.Match) -> str:
    fact1, fact2 = match.groups()
    return str(float(fact1) + float(fact2))


def _sub_handle(match: re.Match) -> str:
    fact1, fact2 = match.groups()
    return str(float(fact1) - float(fact2))


class ExpressionPatterns(Enum):
    PARENTHESIS = (re.compile(r'\(([^\(]+?)\)', re.IGNORECASE), _parenthesis_handle, 5)
    DICE = (re.compile(r'(\d+)d(\d+)', re.IGNORECASE), _dice_generate, 4)
    DICE_SPE = (re.compile(r'(\d+)d\{(.+?)\}', re.IGNORECASE), _dice_spe_generate, 3)
    MUL = (re.compile(r'([\d\.]+)\*([\d\.]+)', re.IGNORECASE), _mul_handle, 1)
    DIV = (re.compile(r'([\d\.]+)\/([\d\.]+)', re.IGNORECASE), _div_handle, 1)
    DIVENT = (re.compile(r'(\d+)\/\/(\d+)', re.IGNORECASE), _divent_handle, 2)
    MOD = (re.compile(r'(\d+)\%(\d+)', re.IGNORECASE), _mod_handle, 2)
    ADD = (re.compile(r'([\d\.]+)\+([\d\.]+)', re.IGNORECASE), _add_handle, 0)
    SUB = (re.compile(r'([\d\.]+)\-([\d\.]+)', re.IGNORECASE), _sub_handle, 0)

    def __new__(cls, value: re.Pattern, func: Callable[[re.Match], str], weight: int) -> Self:
        self = object.__new__(cls)
        self._value_ = value
        return self

    def __init__(self, value: re.Pattern, func: Callable[[re.Match], str], weight: int) -> None:
        self._func = func
        self._weight = weight

    @property
    def weight(self) -> int:
        return self._weight

    def __call__(self, expr: str) -> str:
        while self.value.search(expr):
            expr = self.value.sub(self._func, expr)
        return expr

    @classmethod
    def get_ordered(cls) -> list[Self]:
        ls = list(cls)
        ls.sort(key=lambda x: x.weight, reverse=True)
        return ls


class Expression:
    def __init__(self, expr: str) -> None:
        self._raw = expr

    def __call__(self) -> str:
        expr = self._raw.replace(' ', '')

        for pattern in ExpressionPatterns.get_ordered():
            expr = pattern(expr)

        return expr
