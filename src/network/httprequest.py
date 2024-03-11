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


from typing import Optional, Self
from enum import Enum, IntEnum, auto
import functools
import aiohttp
from .exceptions import HTTPException
from .statuscode import HttpRequestStatus, HttpErrorCode


class HttpResultType(IntEnum):
    NONE = 0
    TEXT = auto()
    JSON = auto()


class HttpRequest:
    USE_HTTPS_BY_DEFAULT = False

    def __init__(self, url: str, status: int, *, result: Optional[str | dict] = None) -> None:
        self.url = url
        self.status = HttpRequestStatus.get_status(status)
        self.error_code: Optional[HttpErrorCode] = None
        self.result = result
        self.whitelisted: list[HttpErrorCode] = []

        if self.status.ko:
            self.error_code = HttpErrorCode.get_code_from_int(status)

    def whitelist(self, *errors: HttpErrorCode) -> Self:
        self.whitelisted = list(errors)
        return self

    def raise_errors(self, *, raise_redirect: bool = True, raise_client_error: bool = True) -> None:
        if self.error_code and self.error_code not in self.whitelisted:
            exc = HTTPException(self.error_code, self.url)

            if raise_redirect and self.error_code.is_redirect():
                raise exc
            if raise_client_error and self.error_code.is_client_error():
                raise exc
            if self.error_code.is_server_error():
                raise exc

    @classmethod
    async def _process_result(
            cls,
            url: str,
            response: aiohttp.ClientResponse, *,
            has_result: bool = True,
            json: bool = True
    ) -> Self:
        status = HttpRequestStatus.get_status(response.status)

        if status.ko:
            status = HttpErrorCode.get_code_from_int(response.status)
            return cls(url, response.status)

        if has_result:
            if json:
                result = await response.json()
            else:
                result = await response.text()

            return cls(url, response.status, result=result)

        return cls(url, response.status)

    @classmethod
    async def get(
            cls,
            url: str, *,
            query: Optional[dict[str, str]] = None,
            headers: Optional[dict[str, str]] = None,
            json: bool = True,
            https: Optional[bool] = None
    ) -> Self:
        async with aiohttp.ClientSession() as session:
            getter = session.get

            if headers:
                getter = functools.partial(getter, headers=headers)
            if query:
                getter = functools.partial(getter, params=query)

            async with getter(url, ssl=https if https is not None else cls.USE_HTTPS_BY_DEFAULT) as response:
                return await cls._process_result(url, response, json=json)

    @classmethod
    async def post(
            cls,
            url: str,
            body: dict, *,
            headers: Optional[dict[str, str]] = None,
            expected_result: HttpResultType = HttpResultType.NONE,
            https: Optional[bool] = None
    ) -> Self:
        async with aiohttp.ClientSession() as session:
            poster = session.post

            if headers:
                poster = functools.partial(poster, headers=headers)

            async with poster(url, json=body, ssl=https if https is not None else cls.USE_HTTPS_BY_DEFAULT) as response:
                return await cls._process_result(
                    url,
                    response,
                    has_result=bool(expected_result),
                    json=expected_result == HttpResultType.JSON
                )

    @classmethod
    async def put(
            cls,
            url: str, *,
            body: Optional[dict] = None,
            headers: Optional[dict[str, str]] = None,
            expected_result: HttpResultType = HttpResultType.NONE,
            https: Optional[bool] = None
    ) -> Self:
        async with aiohttp.ClientSession() as session:
            putter = session.put

            if headers:
                putter = functools.partial(putter, headers=headers)
            if body:
                putter = functools.partial(putter, json=body)

            async with putter(url, ssl=https if https is not None else cls.USE_HTTPS_BY_DEFAULT) as response:
                return await cls._process_result(
                    url,
                    response,
                    has_result=bool(expected_result),
                    json=expected_result == HttpResultType.JSON
                )

    @classmethod
    async def delete(
            cls,
            url: str, *,
            body: Optional[dict] = None,
            headers: Optional[dict[str, str]] = None,
            expected_result: HttpResultType = HttpResultType.NONE,
            https: Optional[bool] = None
    ) -> Self:
        async with aiohttp.ClientSession() as session:
            deleter = session.delete

            if headers:
                deleter = functools.partial(deleter, headers=headers)
            if body:
                deleter = functools.partial(deleter, json=body)

            async with deleter(url, ssl=https if https is not None else cls.USE_HTTPS_BY_DEFAULT) as response:
                return await cls._process_result(
                    url,
                    response,
                    has_result=bool(expected_result),
                    json=expected_result == HttpResultType.JSON
                )


class HTTP(Enum):
    GET = HttpRequest.get
    POST = HttpRequest.post
    PUT = HttpRequest.put
    DELETE = HttpRequest.delete

    async def __call__(self, *args, **kwargs) -> HttpRequest:
        return await self.value(*args, **kwargs)
