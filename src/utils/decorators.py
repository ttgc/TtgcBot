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

from exceptions import DeprecatedException, AlreadyCalledFunctionException
from setup.logconfig import get_logger

def singleton(cl):
    instances = {}
    def get_instance():
        if cl not in instances:
            instances[cl] = cl()
        return instances[cl]
    return get_instance

def call_once(raise_error=False):
    def call_once_decorator(fct):
        called = {}
        def call_fct(*args, **kwargs):
            if fct not in called:
                called[fct] = fct(*args, **kwargs)
            elif raise_error:
                raise AlreadyCalledFunctionException(fct)
            return called[fct]
        return call_fct
    return call_once_decorator

def deprecated(reason, *, raise_error=True, logger=None):
    def deprecated_decorator(fct):
        logMethod = logger if logger else get_logger().warn
        logMethod(f"Deprecated function/class: {fct}\nReason: {reason}")

        def deprecated_call(*args, **kwargs):
            exception = DeprecatedException(fct, reason, *args, **kwargs)
            if raise_error:
                raise exception
            logMethod(exception)
            return fct(*args, **kwargs)
        return deprecated_call
    return deprecated_decorator
