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
from enum import IntEnum
from lang import Language


class HttpRequestStatus(IntEnum):
    INFO = 1
    SUCCESS = 2
    REDIRECT = 3
    CLIENT_ERROR = 4
    SERVER_ERROR = 5

    @classmethod
    def get_status(cls, code: int) -> Self:
        return cls(code // 100)

    @property
    def ok(self) -> bool:
        return self <= 2

    @property
    def ko(self) -> bool:
        return not self.ok


class HttpErrorCode(IntEnum):
    UNKNOWN = -1

    MULTIPLE_CHOICE = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    TOO_MANY_REDIRECT = 310

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    REQUEST_URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_UNSATISFIABLE = 416
    EXPECTATION_FAILED = 417
    I_AM_A_TEAPOT = 418
    BAD_MAPPING = 421
    UNAVAILABLE_FOR_LEGAL_REASON = 451

    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    BANDWIDTH_LIMIT_EXCEEDED = 509

    @classmethod
    def get_code_from_int(cls, code: int) -> Self:
        try:
            return cls(code)
        except ValueError:
            return cls.UNKNOWN # type: ignore

    def is_redirect(self) -> bool:
        return self.value // 100 == 3

    def is_client_error(self) -> bool:
        return self.value // 100 == 4

    def is_server_error(self) -> bool:
        return self.value // 100 == 5

    def is_unknown(self) -> bool:
        return self == self.__class__.UNKNOWN

    def to_string(self, lang: Language, message: Optional[str] = None, **kwargs) -> str:
        if message is None:
            message = str(kwargs)

        cls = self.__class__
        mapped_errors = {
            cls.PERMANENT_REDIRECT: cls.MOVED_PERMANENTLY,
            cls.FOUND: cls.MOVED_PERMANENTLY,
            cls.TEMPORARY_REDIRECT: cls.MOVED_PERMANENTLY,
            cls.USE_PROXY: cls.UNKNOWN,
            cls.NOT_MODIFIED: cls.UNKNOWN,
            cls.PAYMENT_REQUIRED: cls.UNKNOWN,
            cls.NOT_ACCEPTABLE: cls.UNKNOWN,
            cls.PROXY_AUTHENTICATION_REQUIRED: cls.UNAUTHORIZED,
            cls.REQUEST_URI_TOO_LONG: cls.REQUEST_ENTITY_TOO_LARGE,
            cls.GONE: cls.MOVED_PERMANENTLY,
            cls.LENGTH_REQUIRED: cls.UNKNOWN,
            cls.PRECONDITION_FAILED: cls.UNKNOWN,
            cls.REQUESTED_RANGE_UNSATISFIABLE: cls.UNKNOWN,
            cls.EXPECTATION_FAILED: cls.UNKNOWN,
            cls.BAD_MAPPING: cls.UNKNOWN,
            cls.GATEWAY_TIMEOUT: cls.REQUEST_TIMEOUT
        }

        final_error = mapped_errors.get(self, self)
        err_details = lang[f"http_{final_error if not final_error.is_unknown() else 'unknown'}"]
        return err_details.format(message)


type HttpStatus = HttpRequestStatus | HttpErrorCode
