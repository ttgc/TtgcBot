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


import itertools
from .dice import AnyDice


class DiceCombinator:
    def __init__(self, count: int, dice: AnyDice, *, fgroup_count: int = -1, initial_generate: bool = True) -> None:
        self._count = count
        self._dice = dice
        self._generated: list[int] = []
        self._fgroup_count = fgroup_count if fgroup_count > 0 else self._count // 2
        self.generation_paused = not initial_generate
        self._combinations = self._internal_generate()

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        self._count = value
        self()

    @property
    def dice(self) -> AnyDice:
        return self._dice

    @dice.setter
    def dice(self, value: AnyDice) -> None:
        self._dice = value
        self()

    @property
    def generated(self) -> list[int]:
        return self._generated[:]

    @property
    def groups_count(self) -> tuple[int, int]:
        return self._fgroup_count, self.count - self._fgroup_count

    def set_fgroup_count(self, value: int) -> None:
        self._fgroup_count = value
        self()

    @property
    def first_group(self) -> list[int]:
        return [i for i, _ in self._combinations]

    @property
    def second_group(self) -> list[int]:
        return [i for _, i in self._combinations]

    @property
    def combinations(self) -> set[tuple[int, int]]:
        return self._combinations.copy()

    @property
    def total(self) -> int:
        return sum(self.generated)

    def __len__(self) -> int:
        return self.count

    def __call__(self) -> set[tuple[int, int]]:
        self._combinations = self._internal_generate()
        return self.combinations

    def _internal_generate(self) -> set[tuple[int, int]]:
        if self.generation_paused:
            return set()

        self._generated = [self._dice() for _ in range(self._count)]
        total = self.total
        combi = itertools.combinations(self.generated, self._fgroup_count)
        values = [(sum(i), total - sum(i)) for i in combi]
        return set([(k, i) if k < i else (i, k) for i, k in values])
