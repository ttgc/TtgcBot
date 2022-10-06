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

from enum import Enum
import typing

class ViewResult:
    """Wrapper to determines a view's result"""

    def __init__(self, value: int, *, is_success: typing.Optional[bool] = None):
        """
        ViewResult(value, *, is_success)

        Parameters:
            value (int): the view's result identifier
            is_success (Optional[bool]): determines if the view's result is a success or not. If not provided the value will be used instead
        """
        self._value = value
        self._is_success = is_success if is_success is not None else bool(value)

    def __bool__(self):
        """Returns if the view's result is a success or not"""
        return self.is_success

    def __int__(self):
        """Returns the view's result value"""
        return self.value

    @property
    def value(self):
        """Get the view's result value"""
        return self._value

    @property
    def is_success(self):
        """Get if the view's result is a success or not"""
        return self._is_success


class DefaultViewResults(Enum):
    """Enumeration for default view's results"""

    NONE = ViewResult(-1, is_success=False)
    CANCEL = ViewResult(0)
    DEFAULT = ViewResult(0, is_success=True)
    SUBMIT = ViewResult(1)

    def __bool__(self):
        """Return if the view's result is a success or not"""
        return self.value.is_success

    def __int__(self):
        """Return the view's result value"""
        return self.result_code

    @property
    def result_code(self):
        """Get the view's result value"""
        return self.value.value
