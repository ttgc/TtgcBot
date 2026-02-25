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


from typing import Optional
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class CharacterIdentityDTO:
    charkey: str
    member: Optional[int] = None
    selected: bool = False
    dead: bool = False

    def __eq__(self, value: str) -> bool:
        return self.charkey == value

    def __ne__(self, value: str) -> bool:
        return not self.__eq__(value)


@dataclass(kw_only=True)
class CharacterListDTO:
    characters: list[CharacterIdentityDTO] = field(default_factory=list)

    @property
    def active_characters(self) -> dict[int, CharacterIdentityDTO]:
        return {
            char.member: char for char in self.characters \
                if char.selected and not char.dead and char.member
        }

    def __len__(self) -> int:
        return len(self.characters)

    def __getitem__(self, member_id: int) -> list[CharacterIdentityDTO]:
        return [char for char in self.characters if char.member == member_id]

    def __contains__(self, item: str) -> bool:
        return any(char == item for char in self.characters)

    def find(self, key: str) -> Optional[CharacterIdentityDTO]:
        for x in self.characters:
            if x == key:
                return x
        return None
