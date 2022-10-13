#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017  Thomas PIOT
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

from enum import Enum

class Gamemods(Enum):
    UNDEFINED = (-1, 'undefined', 'U')
    OFFENSIVE = (0, 'offensive', 'O')
    DEFENSIVE = (1, 'defensive', 'D')
    ILLUMINATION = (2, 'illumination', 'I')
    SEPULCHRAL = (3, 'sepulchral', 'S')

    def __int__(self):
        return self.index

    def __str__(self):
        return self.name

    @property
    def index(self):
        return self.value[0]

    @property
    def name(self):
        return self.value[1]

    @property
    def charcode(self):
        return self.value[2]

    @classmethod
    def from_str(cl, name):
        for gm in cl:
            if str(gm) == name: return gm
        return cl.UNDEFINED

    @classmethod
    def from_int(cl, value):
        for gm in cl:
            if int(gm) == value: return gm
        return cl.UNDEFINED

    @classmethod
    def from_charcode(cl, charcode):
        for gm in cl:
            if gm.charcode == charcode: return gm
        return cl.UNDEFINED


class TagList(Enum):
    CHARSET = [
        "name", "pv", "pm", "strength", "spirit", "charisma", "agility",
        "precision", "luck", "intuition", "mental", "karma", "gamemod",
        "money", "pilot"
    ]

    PETSET = [
        "name", "pv", "pm", "strength", "spirit", "charisma", "agility",
        "precision", "luck", "instinct", "gamemod", "species"
    ]

    CHARUPDATE = ["pv", "pm", "mental", "karma", "money", "light_point", "dark_point"]
    PETUPDATE = ["pv", "pm", "karma"]
