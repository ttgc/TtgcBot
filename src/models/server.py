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
from network.httprequest import HTTP, HttpResultType
from network.resources import pull_resource
from network.statuscode import HttpErrorCode
from network.exceptions import HTTPException
from config import Log
from utils.decorators import catch
from utils import try_parse_int


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
        async with API('/api/server/{serverID}') as api:
            response = await api(HTTP.GET, f'/api/Server/{self.id}')
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

    @catch(HTTPException, error_value=False, logger=Log.error, asynchronous=True)
    async def update_roles(
            self,
            requester: int,
            requester_role: Optional[int], *,
            admin_role: Optional[int] = None,
            mj_role: Optional[int] = None
    ) -> bool:
        async with API('/api/Server/{serverID}/setrole') as api:
            response = await api(
                HTTP.PUT,
                f'/api/Server/{self.id}/setrole',
                requester=requester,
                role=requester_role,
                body={
                    'admin': admin_role,
                    'mj': mj_role
                }
            )
            response.raise_errors()
            return response.status.ok

    @catch(HTTPException, error_value=False, logger=Log.error, asynchronous=True)
    async def update_prefix(self, requester: int, requester_role: Optional[int], prefix: str) -> bool:
        async with API('/api/server/{serverID}/setprefix') as api:
            response = await api(
                HTTP.PUT,
                f'/api/server/{self.id}/setprefix',
                requester=requester,
                role=requester_role,
                body={'prefix': prefix}
            )
            response.raise_errors()
            return response.status.ok

    @catch(HTTPException, error_value=[], logger=Log.error, asynchronous=True)
    @classmethod
    async def get_server_list(cls) -> list[Self]:
        async with API('/api/server/list') as api:
            response = await api(HTTP.GET, '/api/Server/list')
            response.raise_errors()

        if response.status.ok and response.result and isinstance(response.result, dict):
            return [cls(x) for x in response.result.get('servers', [])]
        return []

    @catch(HTTPException, error_value=None, logger=Log.warn, asynchronous=True)
    @staticmethod
    async def purge(days: int) -> int:
        async with API('/api/server/purge') as api:
            response = await api(HTTP.DELETE, '/api/Server/purge', body={'days': days}, expected_result=HttpResultType.TEXT)
            response.raise_errors()

        return try_parse_int(str(response.result), default_value=-1)
