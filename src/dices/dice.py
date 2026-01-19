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


from random import randint
from enum import IntEnum
from typing import Any


def roll(sides: int) -> int:
    return randint(1, sides)


class Dice(IntEnum):
    COIN = 2
    D2 = 2
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

    def __call__(self) -> int:
        return roll(self.value)


class CustomDice:
    def __init__(self, sides: int) -> None:
        self.sides = sides

    def __call__(self) -> int:
        return roll(self.sides)


type AnyDice = Dice | CustomDice


def get_dice(sides: int) -> AnyDice:
    return Dice(sides) if sides in Dice else CustomDice(sides)
