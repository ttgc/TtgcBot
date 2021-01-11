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

import time
from src.utils.singleton import singleton

@singleton
class DataCache:
    def __init__(self):
        self._cache = {}
        self._clock = {}
        self._mappeditem = {}
        self.maxTime = 3600

    def __getitem__(self, res):
        res = self._mappeditem.get(res, res)
        if res in self._cache and time.clock() - self._clock[res] > self.maxTime:
            self._cache.pop(res)
            self._clock.pop(res)
        return self._cache.get(res, None)

    def __setitem__(self, res, value):
        res = self._mappeditem.get(res, res)
        self._cache[res] = value
        self._clock[res] = time.clock()

    def clear(self):
        self._cache = {}
        self._clock = {}

    def setTimeLimit(self, time):
        self.maxTime = time

    def remove(self, res, remove_mapped_items=False):
        res = self._mappeditem.get(res, res)
        if res in self._cache:
            self._cache.pop(res)
            self._clock.pop(res)
        if remove_mapped_items:
            self.removemapdest(res)

    def mapitems(self, res, *tomap):
        for i in tomap:
            if i not in self._cache:
                self._mappeditem[i] = to

    def removemapsrc(self, mappedres):
        if mappedres in self._mappeditem:
            self._mappeditem.pop(mappedres)

    def removemapdest(self, res):
        ls = []
        for i, k in self._mappeditem.items():
            if k == res: ls.append(i)
        for i in ls:
            self.removemapsrc(i)
