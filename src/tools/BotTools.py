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

import discord
import asyncio
from discord.ext import commands
from src.tools.datahandler.APIManager import *
from src.utils.decorators import deprecated
from src.utils.config import Config
import src.tools.Character as ch
import src.tools.CharacterUtils as chutil

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

async def addserver(server):
    info = await self.api(RequestType.PUT, "Server/{}/join".format(server.id), resource="SRV://{}".format(server.id))

    if info.status // 100 != 2:
        raise APIException("Server join error", srv=server.id, code=info.status)
    return DBServer(server.id)

async def purgeservers(days_):
    info = await self.api(RequestType.DELETE, "Server/purge", hasResult=True, jsonResult=False, body={"days": days_})

    if info.status // 100 != 2:
        raise APIException("Server purge error", code=info.status)
    return int(info.result)

class DBJDR:
    async def __init__(self, srvid, channelid, requester, requesterRole):
        self.server = srvid
        self.requester = requester
        self.requesterRole = requesterRole
        self._initialChannelID = channelid

        info = await self.api(RequestType.GET, "JDR/{}/{}".format(self.server, self._initialChannelID),
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Unable to find JDR", srv=self.server, channel=self._initialChannelID, code=info.status)

        self.creation_date = info.result.get("creation", None)
        self.pjs = info.result.get("players", -1)
        self.mj = info.result.get("owner", self.requester)
        self.channel = info.result.get("channel", self._initialChannelID)
        self.extensions = info.result.get("extensions", [])

        cache = DataCache()
        for i in [self.channel] + self.extensions:
            if i != self._initialChannelID:
                cache.mapitems("SRV://{}/{}".format(self.server, self._initialChannelID), "SRV://{}/{}".format(self.server, i))

    async def delete(self):
        info = await self.api(RequestType.DELETE, "JDR/delete", body={"server": self.server, "channel": self.channel},
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR delete error", srv=self.ID, channel=self.channel, code=info.status)
        DataCache.remove("SRV://{}/{}".format(self.server, self._initialChannelID), True)

    async def MJtransfer(self, member_id):
        info = await self.api(RequestType.PUT, "JDR/transfer/{}/{}".format(self.server, self.channel),
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole,
            body={"master": member_id})

        if info.status // 100 != 2:
            raise APIException("MJ transfer error", srv=self.ID, channel=self.channel, oldmj=self.mj, newmj=member_id, code=info.status)
        self.mj = member_id

    async def copy(self, channel_id, *extensions):
        reqbody = {
            "server": self.server,
            "from": self.channel,
            "to": channel_id,
            "extensions": list(extensions)
        }

        info = await self.api(RequestType.POST, "JDR/copy", body=reqbody,
            resource="SRV://{}/{}".format(self.server, channel_id), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR copy error", srv=self.ID, channel=self.channel, tochan=channel_id, code=info.status)
        return DBJDR(self.server, channel_id, self.requester, self.requesterRole)

    async def charcreate(self, chardbkey, race, classe, **kwargs):
        reqbody = {
            "race": race,
            "class_": classe,
            "server": self.server,
            "channel": self.channel,
            "key": chardbkey,
            "data": {
                "name": kwargs.get("name", chardbkey),
                "pv": kwargs.get("pv", 1)
                "pm": kwargs.get("pm", 1)
                "strength": kwargs.get("str", 50),
                "spirit": kwargs.get("spr", 50),
                "charisma": kwargs.get("cha", 50),
                "agility": kwargs.get("agi", 50),
                "precision": kwargs.get("prec", 50),
                "luck": kwargs.get("luck", 50),
                "intuition": kwargs.get("int", 50),
                "mental": kwargs.get("mental", 100),
                "karma": kwargs.get("karma", 0),
                "gamemod": kwargs.get("gm", "offensive"),
                "affiliation": kwargs.get("affiliation", None),
                "money": kwargs.get("money", 0),
                "hybrid": kwargs.get("hybrid", None),
                "symbiont": kwargs.get("symbiont", None),
                "pilot": {
                    "astral": kwargs.get("pa", -1),
                    "planet": kwargs.get("pp", -1)
                }
            }
        }

        info = await self.api(RequestType.POST, "Character/create", body=reqbody,
            resource="SRV://{}/{}/{}".format(self.server, self._initialChannelID, chardbkey), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Char create error", srv=self.ID, channel=self.channel, charkey=chardbkey, code=info.status)

    async def chardelete(self, chardbkey):
        info = await self.api(RequestType.DELETE, "Character/delete/{}/{}/{}".format(self.server, self.channel, chardbkey),
            resource="SRV://{}/{}/{}".format(self.server, self._initialChannelID, chardbkey), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Char delete error", srv=self.ID, channel=self.channel, charkey=chardbkey, code=info.status)

    async def extend(self, channel_id, *other_channels):
        reqbody = {
            "server": self.server,
            "from": self.channel,
            "to": [channel_id] + list(other_channels)
        }

        info = await self.api(RequestType.POST, "JDR/extend", body=reqbody,
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR extend error", srv=self.ID, channel=self.channel, code=info.status)
        self.extensions.append(channel_id)
        self.extensions += list(other_channels)
        cache = DataCache()
        for i in [channel_id] + list(other_channels):
            cache.mapitems("SRV://{}/{}".format(self.server, self._initialChannelID), "SRV://{}/{}".format(self.server, i))

    async def unextend(self, channel_id, *other_channels):
        reqbody = {
            "server": self.server,
            "from": self.channel,
            "to": [channel_id] + list(other_channels)
        }

        info = await self.api(RequestType.DELETE, "JDR/unextend", body=reqbody,
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR unextend error", srv=self.ID, channel=self.channel, code=info.status)
        for channel in [channel_id] + list(other_channels):
            if channel in self.extensions: self.extensions.remove(channel)
        DataCache().remove("SRV://{}/{}".format(self.server, self._initialChannelID), True)

    async def unextend_all(self):
        reqbody = {
            "server": self.server,
            "channel": self.channel
        }

        info = await self.api(RequestType.DELETE, "JDR/unextend/all", body=reqbody,
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR unextend all error", srv=self.ID, channel=self.channel, code=info.status)
        self.extensions = []
        DataCache().remove("SRV://{}/{}".format(self.server, self._initialChannelID), True)

    def get_character(self,charkey):
        db = Database()
        cur = db.call("get_character",dbkey=charkey,idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find character")
        rawchar = cur.fetchone()
        db.close()
        stat = [rawchar[19],rawchar[24],rawchar[22],rawchar[20],rawchar[21],rawchar[23],rawchar[25]]
        gm = ch.Character.gm_map_chartoint[rawchar[28].upper()]
        gmdefault = ch.Character.gm_map_chartoint[rawchar[29].upper()]
        inv = chutil.Inventory()
        inv.loadfromdb(rawchar[30])
        pets = {}
        db = Database()
        cur = db.call("get_pets",dbkey=rawchar[0],idserv=self.server,idchan=self.channel)
        if cur is not None:
            for i in cur:
                gmpet = ch.Character.gm_map_chartoint[i[24].upper()]
                gmpetdefault = ch.Character.gm_map_chartoint[i[25].upper()]
                pets[i[0]] = ch.Pet(petkey=i[0],charkey=rawchar[0],name=i[1],espece=i[2],
                                    PVm=i[5],PMm=i[7],force=i[8],esprit=i[9],
                                    charisme=i[10],agilite=i[11],karma=i[12],
                                    stat=[i[14],i[19],i[17],i[15],i[16],i[18],i[20]],mod=gmpet,
                                    PV=i[4],PM=i[6],default_mod=gmpetdefault,
                                    instinct=i[13],lvl=i[3],prec=i[26],luck=i[27])
        db.close()
        db = Database()
        cur = db.call("get_skill",dbkey=rawchar[0],idserv=self.server,idchan=self.channel)
        skls = []
        if cur is not None:
            for i in cur:
                skls.append(chutil.Skill(i[0]))
        db.close()
        char = ch.Character(charkey=rawchar[0],name=rawchar[1],lore=rawchar[2],
                            lvl=rawchar[3],PV=rawchar[4],PVm=rawchar[5],PM=rawchar[6],
                            PMm=rawchar[7],force=rawchar[8],esprit=rawchar[9],
                            charisme=rawchar[10],furtivite=rawchar[11],karma=rawchar[12],
                            default_karma=rawchar[13],money=rawchar[14],lp=rawchar[15],
                            dp=rawchar[16],intuition=rawchar[17],mentalhealth=rawchar[18],
                            stat=stat,mod=gm,default_mod=gmdefault,inventory=inv,
                            linked=rawchar[31],pet=pets,skills=skls,dead=rawchar[32],
                            classe=rawchar[33],selected=rawchar[34],xp=rawchar[35],
                            prec=rawchar[36],luck=rawchar[37],
                            org=chutil.retrieveOrganization(rawchar[38]),
                            hybrid=rawchar[39], symbiont=rawchar[40],
                            planet_pilot=rawchar[41], astral_pilot=rawchar[42])
        char.bind(self)
        return char

    async def charlist(self):
        info = await self.api(RequestType.GET, "Character/{}/{}".format(self.server, self.channel),
            resource="SRV://{}/{}".format(self.server, self.channel), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Character list error", srv=self.ID, channel=self.channel, code=info.status)

        return info.result

    @deprecated(raise_error=False)
    async def get_charbase(self):
        chars = await self.charlist()
        ls = chars.get("characters", [])
        charbase = []
        for i in ls:
            character = await self.get_character(i)
            charbase.append(character)
        return charbase

    async def get_serverinfo(self):
        srv = await DBServer(self.server)
        return srv

    async def set_finalizer_field(self, **fields):
        reqbody = {
            "server": self.server,
            "channel": self.channel,
            "fields": []
        }

        for i, k in fields.items():
            reqbody["fields"].append({"title": i, "content": k})

        info = await self.api(RequestType.POST, "Finalize/set", body=reqbody,
            resource="SRV://{}/{}/finalize".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Finalize set error", srv=self.ID, channel=self.channel, fields=fields, code=info.status)

    async def del_finalizer_field(self, *fields):
        reqbody = {
            "fields": list(fields)
        }

        info = await self.api(RequestType.DELETE, "Finalize/delete/{}/{}".format(self.server, self.channel), body=reqbody,
            resource="SRV://{}/{}/finalize".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Finalize delete error", srv=self.ID, channel=self.channel, fields=fields, code=info.status)

    async def get_finalizer(self):
        info = await self.api(RequestType.GET, "Finalize/{}/{}".format(self.server, self.channel),
            resource="SRV://{}/{}/finalize".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Finalize set error", srv=self.ID, channel=self.channel, fields=fields, code=info.status)

        ls = []
        for i in info.result.get("fields", []):
            ls.append((i.get("title"), i.get("content")))
        return ls

class DBMember:
    def __init__(self,ID):
        self.ID = ID
        db = Database()
        cur = db.execute("SELECT * FROM Membre WHERE id_member = %(idmemb)s;",idmemb=ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the member")
        info = cur.fetchone()
        if info is None:
            db.close(True)
            raise DatabaseException("unexisting member")
        db.close()
        self.perm = info[1]

    def is_owner(self):
        return self.perm.upper() == "O"

    def is_manager(self):
        return (self.perm.upper() == "M" or self.is_owner())

    def is_premium(self):
        return self.perm.upper() != "N"

    def is_blacklisted(self):
        db = Database()
        cur = db.execute("SELECT COUNT(*) FROM blacklist WHERE id_member = %(idmemb)s;",idmemb=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to retrieve blacklisting")
        blacklisted = True
        if cur.fetchone()[0] == 0:
            blacklisted = False
        db.close()
        rs = ""
        if blacklisted:
            db = Database()
            cur = db.execute("SELECT reason FROM blacklist WHERE id_member = %(idmemb)s;",idmemb=self.ID)
            if cur is None:
                db.close(True)
                raise DatabaseException("unable to find reason for blacklisting")
            rs = cur.fetchone()[0]
            db.close()
        return blacklisted,rs

    def unblacklist(self):
        if not self.is_blacklisted()[0]: return
        db = Database()
        db.call("switchblacklist",idmemb=self.ID,eventual_reason="")
        db.close()

def grantuser(memberid,permcode):
    db = Database()
    db.call("grantperms",idmemb=memberid,perm=permcode)
    db.close()

def blacklist(memberid,reason):
    try:
        mb = DBMember(memberid)
        if mb.is_blacklisted()[0]: return
    except DatabaseException: pass
    db = Database()
    db.call("switchblacklist",idmemb=memberid,eventual_reason=reason)
    db.close()
    return DBMember(memberid)

def setuserlang(memberid,lang):
    db = Database()
    db.call("setlang",idmemb=memberid,lg=lang.upper())
    db.close()

def getuserlang(memberid):
    db = Database()
    cur = db.call("getlang",idmemb=memberid)
    lang = cur.fetchone()[0]
    db.close()
    return lang
