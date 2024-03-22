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
class ServerDTO:
    id: int
    admin_role: Optional[int] = None
    mj_role: Optional[int] = None
    prefix: str = '/'

    def __init__(self, server_id: int) -> None:
        self.id = server_id
        self.fetch = pull_resource(f'SERVER://{self.id}', ttl=168)(self.fetch)

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch(self) -> Optional[Self]:
        async with API('/api/server/{serverID}', requester=self.id) as api:
            response = await api(HTTP.GET, f'/api/Server/{self.id}', requester=self.id) # type: ignore

        response.whitelist(HttpErrorCode.NOT_FOUND, HttpErrorCode.FORBIDDEN)
        response.raise_errors()

        if response.status.ko:
            Log.warn('HTTP server fetch failure (%d) for id=%d', response.error_code, self.id)
            return None
        if not response.result or not isinstance(response.result, dict):
            Log.error('HTTP server fetch unexpected result produced for id=%d: %s', self.id, response.result)
            return None

        self.admin_role = response.result.get('adminRole', 0)
        self.mj_role = response.result.get('mjRole', 0)
        self.prefix = response.result.get('prefix', '/')
        return self
