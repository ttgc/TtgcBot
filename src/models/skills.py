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

from datahandler.api import APIManager
from exceptions import APIException
from models.extension import Extension

class Skill:
    def __init__(self, ID, name, descr, origin, extension):
        self.ID = ID
        self.name = name
        self.description = descr
        self.origine = origin
        self.extension = extension

    def __str__(self):
        return self.description if self.description is not None else ""

    @classmethod
    async def skillsearch(cl, *, skname=None, origin=None, universe=None, world=None, api=None, nologin=False):
        if api is None:
            api = APIManager()
            nologin = False

        info = await api(RequestType.GET, "Skills/search", query={"name": skname, "origin": origin, "universe": universe, "world": world}, disable_autologin=nologin)

        if info.status == 404: return []
        if info.status // 100 != 2:
            raise APIException("Skill info get error", srv=srv, channel=channel, name=skname, origin=origin, universe=universe, world=world, code=info.status)

        skls = []
        for i in info.result.get("skills", [info.result]):
            ext = Extension(i.get("extension", {}).get("universe", "unknown"), i.get("extension", {}).get("world", "unknown"))
            skls.append(cl(i.get("id", -1), i.get("name", ""), i.get("description", None), i.get("origin", ""), ext))
        return skls

    @staticmethod
    def isskillin(ls, skid):
        for i in ls:
            if i.ID == skid: return True
        return False

    @classmethod
    async def loadfromdb(cl, srv, channel, charkey, requester, requesterRole, *, api=None, nologin=False):
        if api is None:
            api = APIManager()
            nologin = False

        info = await api(RequestType.GET, "Skills/{}/{}/{}".format(srv, channel, charkey),
            resource="SRV://{}/{}/{}".format(srv, channel, charkey), requesterID=requester, roleID=requesterRole, disable_autologin=nologin)

        if info.status // 100 != 2:
            raise APIException("Skill list get error", srv=srv, channel=channel, charkey=charkey, code=info.status)

        skls = []
        for i in info.result:
            ext = Extension(i.get("extension", {}).get("universe", "unknown"), i.get("extension", {}).get("world", "unknown"))
            skls.append(cl(i.get("id", -1), i.get("name", ""), i.get("description", ""), i.get("origin", ""), ext))
        return skls
