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

from discord.ext import commands
from enum import Enum

class HTTPErrorCode(Enum):
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
    def get_code_from_int(cl, code):
        try:
            return cl(code)
        except ValueError:
            return cl.UNKNOWN

    def is_redirect(self):
        return self.value // 100 == 3

    def is_client_error(self):
        return self.value // 100 == 4

    def is_server_error(self):
        return self.value // 100 == 5

    def is_unknown(self):
        return self == self.__class__.UNKNOWN

    def toString(self, lang, message=None, **kwargs):
        if message is None:
            message = str(kwargs)

        cl = self.__class__
        mapped_errors = {
            cl.PERMANENT_REDIRECT: cl.MOVED_PERMANENTLY,
            cl.FOUND: cl.MOVED_PERMANENTLY,
            cl.TEMPORARY_REDIRECT: cl.MOVED_PERMANENTLY,
            cl.USE_PROXY: cl.UNKNOWN,
            cl.NOT_MODIFIED: cl.UNKNOWN,
            cl.PAYMENT_REQUIRED: cl.UNKNOWN,
            cl.NOT_ACCEPTABLE: cl.UNKNOWN,
            cl.PROXY_AUTHENTICATION_REQUIRED: cl.UNAUTHORIZED,
            cl.REQUEST_URI_TOO_LONG: cl.REQUEST_ENTITY_TOO_LARGE,
            cl.GONE: cl.MOVED_PERMANENTLY,
            cl.LENGTH_REQUIRED: cl.UNKNOWN,
            cl.PRECONDITION_FAILED: cl.UNKNOWN,
            cl.REQUESTED_RANGE_UNSATISFIABLE: cl.UNKNOWN,
            cl.EXPECTATION_FAILED: cl.UNKNOWN,
            cl.BAD_MAPPING: cl.UNKNOWN,
            cl.GATEWAY_TIMEOUT: cl.REQUEST_TIMEOUT
        }

        final_error = mapped_errors.get(self, self)
        err_details = lang["http_{}".format(final_error.value if final_error != cl.UNKNOWN else "unknown")]
        return err_details.format(message)

class HTTPException(commands.CommandError):
    def __init__(self, errcode, message=None):
        self.errcode = errcode
        self.message = message if message else "No more details provided"
        super().__init__(str(self))

    def __str__(self):
        return "HTTPException: Error Code {} ({})".format(self.errcode, self.message)

    def parse(self, lang):
        return HTTPErrorCode.get_code_from_int(self.errcode).toString(lang, self.message)

class ManagerException(commands.CommandError):
    def __init__(self, message="Manager exception occured", **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(str(self))

    def __getitem__(self, item):
        return self.kwargs.get(item, None)

    def __str__(self):
        return "ManagerException: {} (with kwargs {})".format(self.message, self.kwargs)

class DatabaseException(ManagerException):
    def __str__(self):
        return "DatabaseException: {} (with kwargs {})".format(self.message, self.kwargs)

class APIException(ManagerException):
    def __str__(self):
        return "APIException: {} (with kwargs {})".format(self.message, self.kwargs)

    def parse(self, lang):
        return HTTPErrorCode.get_code_from_int(self.kwargs.get("code", 502)).toString(lang, None, **self.kwargs)

class DeprecatedException(Exception):
    def __init__(self, fct, *args, **kwargs):
        self.fct = fct
        self.args = args
        self.kwargs = kwargs
        super().__init__(str(self))

    def __str__(self):
        invok = "{}({}, {})".format(self.fct.__name__, list(self.args), dict(self.kwargs))
        invok = invok.replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace(":", "=")
        return "DeprecatedException: The function {} is deprecated\nTried to invoke {}".format(self.fct, invok)

class InternalCommandError(commands.CommandError): pass
