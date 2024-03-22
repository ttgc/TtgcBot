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
from enum import StrEnum
from network.api import API
from network.httprequest import HTTP
from network.resources import pull_resource
from network.statuscode import HttpErrorCode
from network.exceptions import HTTPException
from lang import Language
from config import Log
from utils.decorators import catch, call_once


class MemberPerms(StrEnum):
    NONE = 'None'
    PREMIUM = 'Premium'
    MANAGER = 'Manager'
    OWNER = 'Owner'

    @call_once(False)
    @classmethod
    def get_ordered_list(cls) -> list[Self]:
        return [cls.NONE, cls.PREMIUM, cls.MANAGER, cls.OWNER] # type: ignore

    def __gt__(self, __value: Self) -> bool:
        idx = self.get_ordered_list().index(self)
        idother = self.get_ordered_list().index(__value)
        return idx > idother

    def __ge__(self, __value: str) -> bool:
        return self > __value or self == __value

    def __lt__(self, __value: str) -> bool:
        return not (self >= __value)

    def __le__(self, __value: str) -> bool:
        return self < __value or self == __value


@dataclass
class MemberDTO:
    id: int
    lang: Language = Language.get_default()
    blacklisted: Optional[str] = None
    perms: MemberPerms = MemberPerms.NONE

    def __init__(self, member_id: int) -> None:
        self.id = member_id
        self.fetch = pull_resource(f'MEMBER://{self.id}', ttl=1)(self.fetch)

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch(self) -> Optional[Self]:
        async with API('/api/Member/{memberID}', requester=self.id) as api:
            response = await api(HTTP.GET, f'/api/Member/{self.id}', requester=self.id) # type: ignore

        response.whitelist(HttpErrorCode.NOT_FOUND, HttpErrorCode.FORBIDDEN)
        response.raise_errors()

        if response.status.ko:
            Log.warn('HTTP member fetch failure (%d) for id=%d', response.error_code, self.id)
            return None
        if not response.result or not isinstance(response.result, dict):
            Log.error('HTTP member fetch unexpected result produced for id=%d: %s', self.id, response.result)
            return None

        self.lang = Language.get(response.result.get('language', {}).get('langcode', 'EN'))
        blacklisted: dict = response.result.get('blacklisted', {})
        self.blacklisted = blacklisted.get('reason', '') if blacklisted.get('isBlacklisted', False) else None
        self.perms = MemberPerms(response.result.get('permissions', 'None'))
        return self
