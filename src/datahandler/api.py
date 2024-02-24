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

import base64
import hashlib
import time
import argon2.low_level as argon2
from setup.config import Config
from exceptions import APIException
from network import HTTP, RequestType
from datahandler.cache import DataCache

class APIManager:
    def __init__(self):
        config = Config()
        self.id = config["api-app"]["id"]
        self.appname = config["api-app"]["nom"]
        pwdargs = config["api-app"]["password"]
        rawpwd = "{}-{}".format(pwdargs["pwd"], pwdargs["timestamp"]).encode()
        self._pwd = argon2.hash_secret_raw(rawpwd, bytes(pwdargs["salt"]), time_cost=4, memory_cost=1024, parallelism=8, hash_len=32, type=argon2.Type.ID).hex().upper()
        self.url = config["api-path"]
        self.logged = False
        self._token = None

    async def login(self, requesterID=None, roleID=None, *endpoints):
        if self.logged: self.logout()
        timestamp = time.gmtime()
        tohash = f"{self.id}-{self.appname}-{timestamp.tm_mday:02d}-{timestamp.tm_mon:02d}-{timestamp.tm_year:04d}"
        hash = base64.b64encode(hashlib.sha256(tohash.encode()).digest())
        body = {"app": {"id": self.id, "name": self.appname, "hash": hash.decode(), "pwd": self._pwd}, "endpoints": list(endpoints)}
        if requesterID is not None: body["member"] = requesterID
        if roleID is not None: body["role"] = roleID
        req = await HTTP.post("{}/api/Login".format(self.url), body, hasResult=True, jsonResult=False)
        self.logged = (req.status // 100 == 2)
        if not self.logged:
            raise APIException("Error on login", code=req.status)
        self._token = req.result

    async def logout(self):
        req = await HTTP.delete("{}/api/Logout".format(self.url), headers={"token": self._token})
        if req.status_code // 100 != 2:
            raise APIException("Error on logout", code=req.status)
        self.logged = False
        self._token = None

    async def __call__(self, reqType, endpoint, *, requesterID=None, roleID=None, body={}, query={}, hasResult=False, jsonResult=True, resource=None, forceGet=False, disable_autologin=False):
        cache = DataCache()
        if resource is not None and not forceGet and reqType == RequestType.GET:
            result = cache[resource]
            if result is not None: return result

        if not disable_autologin:
            await self.login(requesterID, roleID, endpoint)

        headers = {"token": self._token}
        if requesterID: headers["member"] = requesterID
        if roleID: headers["role"] = roleID
        result = None

        if reqType == RequestType.GET:
            result = await HTTP.get("{}/api/{}".format(self.url, endpoint), query=query, headers=headers, jsonResult=jsonResult)
        if reqType == RequestType.POST:
            result = await HTTP.post("{}/api/{}".format(self.url, endpoint), body, headers=headers, hasResult=hasResult, jsonResult=jsonResult)
        if reqType == RequestType.PUT:
            body = body if len(body) > 0 else None
            result = await HTTP.put("{}/api/{}".format(self.url, endpoint), body, headers=headers, hasResult=hasResult, jsonResult=jsonResult)
        if reqType == RequestType.DELETE:
            body = body if len(body) > 0 else None
            result = await HTTP.delete("{}/api/{}".format(self.url, endpoint), body, headers=headers, hasResult=hasResult, jsonResult=jsonResult)

        if resource is not None:
            if reqType == RequestType.GET:
                cache[resource] = result
            else:
                cache.remove(resource)

        if not disable_autologin:
            await self.logout()

        return result
