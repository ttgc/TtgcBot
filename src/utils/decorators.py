#!usr/bin/env python3.7
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

from src.utils.exceptions import DeprecatedException

def singleton(cl):
    instances = {}
    def get_instance():
        if cl not in instances:
            instances[cl] = cl()
        return instances[cl]
    return get_instance

def deprecated(raise_error=True, logger=None):
    def deprecated_decorator(fct):
        logMethod = print
        if logger: logMethod = logger
        logMethod("Deprecated function/class : {}".format(fct))

        def deprecated_call(*args, **kwargs):
            exception = DeprecatedException(*args, **kwargs)
            if raise_error:
                raise exception
            logMethod(exception)
            return fct(*args, **kwargs)
        return deprecated_call
    return deprecated_decorator
