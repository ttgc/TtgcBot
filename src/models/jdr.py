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


from typing import Self, Optional
from dataclasses import dataclass
from network.api import API
from network.httprequest import HTTP
from network.resources import pull_resource
from network.statuscode import HttpErrorCode
from network.exceptions import HTTPException
from config import Log
from utils.decorators import catch


@dataclass
class JdrDTO:
    srv_id: int
    chan_id: int
    creation_time: str
    owner_id: int
    player_count: int
    label: str
    extensions: list[int]

    def __init__(self, srv_id: int, chan_id: int, **kwargs) -> None:
        self.srv_id = srv_id
        self.chan_id = chan_id
        self.fetch = pull_resource(f'JDR://{self.srv_id}/{self.chan_id}', ttl=24)(self.fetch)

        self.creation_time = kwargs.get('creation_time', '')
        self.owner_id = kwargs.get('owner_id', 0)
        self.player_count = kwargs.get('player_count', 0)
        self.label = kwargs.get('label', '')
        self.extensions = kwargs.get('extensions', [])

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch(self) -> Optional[Self]:
        async with API('/api/jdr/{serverID}/{channelID}') as api:
            response = await api(HTTP.GET, f'/api/Jdr/{self.srv_id}/{self.chan_id}')
            response.whitelist(HttpErrorCode.NOT_FOUND)
            response.raise_errors()

        if response.status.ko:
            Log.warn('HTTP jdr fetch failure (%d) for id=%d/%d', response.error_code, self.srv_id, self.chan_id)
            return None
        if not response.result or not isinstance(response.result, dict):
            Log.error('HTTP jdr fetch unexpected result produced for id=%d/%d: %s', self.srv_id, self.chan_id, response.result)
            return None

        self.chan_id = response.result.get('channel', self.chan_id)
        self.creation_time = response.result.get('creation', '')
        self.owner_id = response.result.get('owner', 0)
        self.player_count = response.result.get('players', 0)
        self.label = response.result.get('label', '')
        self.extensions = response.result.get('extensions', [])
        return self

    @catch(HTTPException, error_value=[], logger=Log.error, asynchronous=True)
    @classmethod
    async def get_jdr_list(cls, srv_id: int) -> list[Self]:
        async with API('/api/jdr/list/{serverID}') as api:
            response = await api(HTTP.GET, f'/api/jdr/list/{srv_id}')
            response.raise_errors()

        if response.status.ok and response.result and isinstance(response.result, dict):
            return [cls(
                x['server'],
                x['channel'],
                creation_time=x.get('creation', ''),
                owner_id=x.get('owner', 0),
                player_count=x.get('players', 0),
                label=x.get('label', ''),
                extensions=x.get('extensions', [])
            ) for x in response.result.get('jdr', [])]

        return []
