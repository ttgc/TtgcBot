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
from enum import StrEnum


class Emoji(StrEnum):
    X = '❌'
    WHITE_CHECK_MARK = '✅'
    HEAVY_CHECK_MARK = '✔️'
    EQUAL = '🟰'
    PLUS = '➕'
    MINUS = '➖'
    HOURGLASS = '⏳'
    TRACK_PREVIOUS = '⏮️'
    TRACK_NEXT = '⏭️'
    FAST_FORWARD = '⏩'
    REWIND = '⏪'
    HASH = '#️⃣'
    CROSSED_SWORDS = '⚔️'
    SHIELD = '🛡️'
    MUSCLE = '💪'
    GHOST = '👻'
    HEART_EYES = '😍'
    CLOUD_TORNADO = '🌪️'
    DART = '🎯'
    FOUR_LEAF_CLOVER = '🍀'
    EYES = '👀'
    PILL = '💊'
    MAGIC_WAND = '🪄'
    PASSPORT_CONTROL = '🛂'
    ROCKET = '🚀'
    WASTEBASKET = '🗑️'

    @classmethod
    def from_str(cls, string: str) -> Self:
        searched = string.strip(':').upper()

        for emoji in cls:
            if emoji.name == searched:
                return emoji

        raise ValueError(f"'{string}' is not a valid Emoji")
