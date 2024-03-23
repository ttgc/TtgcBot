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


from typing import Optional, Type, Self
from types import TracebackType
import time
import base64
import hashlib
import argon2.low_level as argon2
from config import Config
from config.logger import Log
from .httprequest import HTTP, HttpResultType, HttpRequest


class API:
    def __init__(self, *endpoints: str, requester: Optional[int] = None, requester_role: Optional[int] = None) -> None:
        config = Config()
        self.id: int = config["api-app"]["id"]
        self.appname: str = config["api-app"]["nom"]

        pwdargs = config["api-app"]["password"]
        rawpwd = f'{pwdargs["pwd"]}-{pwdargs["timestamp"]}'.encode()
        self._pwd = argon2.hash_secret_raw(
            rawpwd,
            bytes(pwdargs["salt"]),
            time_cost=4,
            memory_cost=1024,
            parallelism=8,
            hash_len=32,
            type=argon2.Type.ID
        ).hex()

        self.url: str = config["api-path"]
        self.https = self.url.startswith('https')
        self.logged = False
        self._token: Optional[str] = None
        self.authorized_endpoints = list(endpoints)
        self.requester = requester
        self.requester_role = requester_role

    async def __aenter__(self) -> Self:
        if self.logged:
            raise ConnectionError("Cannot enter an API context manager inside another one")

        timestamp = time.gmtime()
        tohash = f"{self.id}-{self.appname}-{time.strftime('%d-%m-%Y', timestamp)}"
        hash = base64.b64encode(hashlib.sha256(tohash.encode()).digest())
        body: dict = {
            "app": {
                "id": self.id,
                "name": self.appname,
                "hash": hash.decode(),
                "pwd": self._pwd,
                "endpoints": self.authorized_endpoints
            }
        }

        response = await HTTP.POST(f"{self.url}/api/Login", body, expected_result=HttpResultType.TEXT, https=self.https)
        response.raise_errors()
        self.logged = response.status.ok
        self._token = str(response.result)
        Log.info("Logged into the API successfully")
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType]
    ) -> None:
        if self._token:
            response = await HTTP.DELETE(f"{self.url}/api/Logout", headers={"token": self._token}, https=self.https)
            response.raise_errors()
            self.logged = False
            self._token = None
            Log.info("Logged out from the API successfully")

        if exc and exc_type:
            Log.error('%s raised when querying API: %s.\n%s', exc_type.__name__, str(exc), str(tb))
            raise exc

    async def __call__(
            self,
            request_type: HTTP,
            endpoint: str,
            *args,
            requester: Optional[int] = None,
            role: Optional[int] = None,
            **kwargs
    ) -> HttpRequest:
        headers: dict = {"token": self._token}

        if requester:
            headers["member"] = requester
        if role:
            headers["role"] = role
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        return await request_type(f"{self.url}/api/{endpoint}", *args, headers=headers, **kwargs)
