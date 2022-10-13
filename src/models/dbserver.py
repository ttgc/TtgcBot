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
from datahandler.api import APIManager
from exception import APIException

class DBServer:
    async def __init__(self, ID):
        self.ID = ID
        self.api = APIManager()
        info = await self.api(RequestType.GET, "Server/{}".format(self.ID), resource="SRV://{}".format(self.ID))
        if info.status // 100 != 2:
            raise APIException("Server not found", srv=self.ID, code=info.status)
        self.mjrole = info.result.get("mjRole", None)
        self.prefix = info.result.get("prefix", '/')
        self.adminrole = info.result.get("adminRole", None)

    async def setmjrole(self, roleid, requester, requesterRole):
        info = await self.api(RequestType.PUT, "Server/{}/setrole".format(self.ID),
            resource="SRV://{}".format(self.ID), requesterID=requester, roleID=requesterRole, body={"mj": roleid, "admin": None})

        if info.status // 100 != 2:
            raise APIException("Server set MJ role error", srv=self.ID, code=info.status)
        self.mjrole = roleid

    async def setadminrole(self, roleid, requester, requesterRole):
        info = await self.api(RequestType.PUT, "Server/{}/setrole".format(self.ID),
            resource="SRV://{}".format(self.ID), requesterID=requester, roleID=requesterRole, body={"mj": None, "admin": roleid})

        if info.status // 100 != 2:
            raise APIException("Server set Admin role error", srv=self.ID, code=info.status)
        self.adminrole = roleid

    async def setprefix(self, prefix, requester, requesterRole):
        info = await self.api(RequestType.PUT, "Server/{}/setprefix".format(self.ID),
            resource="SRV://{}".format(self.ID), requesterID=requester, roleID=requesterRole, body={"prefix": prefix})

        if info.status // 100 != 2:
            raise APIException("Server set prefix error", srv=self.ID, code=info.status)
        self.prefix = prefix

    async def jdrlist(self, requester, requesterRole):
        info = await self.api(RequestType.GET, "JDR/list/{}".format(self.ID),
            resource="SRV://{}/jdrlist".format(self.ID), requesterID=requester, roleID=requesterRole)

        if info.status // 100 != 2:
            raise APIException("Unable to get the jdr list", srv=self.ID, code=info.status)
        return info.result.get("jdr", [])

    async def remove(self, requester, requesterRole):
        info = await self.api(RequestType.PUT, "Server/{}/leave".format(self.ID),
            resource="SRV://{}".format(self.ID), requesterID=requester, roleID=requesterRole)

        if info.status // 100 != 2:
            raise APIException("Server leave error", srv=self.ID, code=info.status)

    async def getJDR(self, channelid, requester, requesterRole):
        jdr = await DBJDR(self.ID, channelid, requester, requesterRole)
        return jdr

    async def jdrstart(self, mjid, requesterRole, *channels):
        if len(channels) == 0:
            raise commands.CommandError("JDR create error: channel list is empty")

        reqbody = {
            "server": self.ID,
            "channel": channels[0],
            "extensions": list(channels[1:]) if len(channels) > 1 else [],
            "owner": mjid
        }

        info = await self.api(RequestType.PUT, "JDR/create",
            resource="SRV://{}//{}".format(self.ID, channelid), requesterID=mjid, roleID=requesterRole, body=reqbody)

        if info.status // 100 != 2:
            raise APIException("JDR create error", srv=self.ID, channel=channels[0], code=info.status)
        return self.getJDR(channelid, mjid, requesterRole)

    @classmethod
    async def addserver(cl, server):
        api = APIManager()
        info = await api(RequestType.PUT, "Server/{}/join".format(server.id), resource="SRV://{}".format(server.id))

        if info.status // 100 != 2:
            raise APIException("Server join error", srv=server.id, code=info.status)
        return cl(server.id)

    @staticmethod
    async def purgeservers(days_):
        api = APIManager()
        info = await api(RequestType.DELETE, "Server/purge", hasResult=True, jsonResult=False, body={"days": days_})

        if info.status // 100 != 2:
            raise APIException("Server purge error", code=info.status)
        return int(info.result)

    @staticmethod
    async def srvlist():
        api = APIManager()
        info = await api(RequestType.GET, "Server/list")

        if info.status // 100 != 2:
            raise APIException("Server list error", code=info.status)
        return info.result.get("servers", [])
