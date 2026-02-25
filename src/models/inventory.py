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


from typing import Self, Optional, TYPE_CHECKING
from dataclasses import dataclass
from network.api import API
from network.httprequest import HTTP
from network.resources import pull_resource
from network.statuscode import HttpErrorCode
from network.exceptions import HTTPException
from config import Log
from utils.decorators import catch
from .enumerations import fetch_gamemods, fetch_extensions
from .member import MemberDTO


if TYPE_CHECKING:
    from .enumerations import BaseGamemods, BaseRaces, BaseClasses, BaseExtensions, BaseOrganizations, BaseSymbionts


def inv_maxsize_from_strength(strength: int) -> float:
    return ((strength // 10) / 10) * 40


@dataclass(kw_only=True)
class ItemDTO:
    name: str
    qte: int = 1
    weight: float = 1.0

    @property
    def stack_size(self) -> float:
        return self.qte * self.weight

    def __iadd__(self, number: int) -> Self:
        self.qte += number
        return self

    def __isub__(self, number: int) -> Self:
        if number > self.qte:
            raise ValueError(f'Cannot remove more than current quantity for item {self.name}')
        self.qte -= number
        return self

    def __imul__(self, number: int) -> Self:
        self.qte *= number
        return self


@dataclass(init=False)
class InventoryDTO:
    id_srv: int
    id_chan: int
    owner: str
    items: list[ItemDTO]
    max_size: float
    shrink_factor: float

    @property
    def size(self) -> float:
        return sum(x.stack_size for x in self.items) * self.shrink_factor

    @property
    def overcharged(self) -> bool:
        return self.size > self.max_size

    @property
    def delta_charge(self) -> float:
        return self.size - self.max_size

    def __init__(self, id_srv: int, id_chan: int, owner: str, max_size: float = 20.0) -> None:
        self.id_srv = id_srv
        self.id_chan = id_chan
        self.owner = owner
        self.items = []
        self.max_size = max_size
        self.shrink_factor = 1.0
        self.fetch = pull_resource(f'CHARACTER://{self.srv_id}/{self.chan_id}/{self.charkey}/inventory', ttl=24)

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch(self) -> Optional[Self]:
        async with API('/api/inventory/{serverID}/{channelID}/{charkey}') as api:
            response = await api(HTTP.GET, f'/api/inventory/{self.id_srv}/{self.id_chan}/{self.owner}')
            response.whitelist(HttpErrorCode.NOT_FOUND)
            response.raise_errors()

        if response.status.ko:
            Log.warn('HTTP character fetch failure (%d) for id=%d/%d/%s', response.error_code, self.id_srv, self.id_chan, self.owner)
            return None
        if not response.result or not isinstance(response.result, dict):
            Log.error('HTTP character fetch unexpected result produced for id=%d/%d/%s: %s', self.id_srv, self.id_chan, self.owner, response.result)
            return None

        self.items = [
            ItemDTO(
                name=x.get('name', ''),
                qte=x.get('quantity', 1),
                weight=x.get('weight', 1.0)
            ) for x in response.result.get('items', [])
        ]
        return self
