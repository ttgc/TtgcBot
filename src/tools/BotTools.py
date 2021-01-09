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
    def __init__(self,srvid,channelid):
        self.server = srvid
        db = Database()
        cur = db.call("get_jdr",idserv=srvid,idchan=channelid)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the JDR")
        info = cur.fetchone()
        db.close()
        self.creation_date = info[2]
        self.pjs = info[3]
        self.mj = info[4]
        self.channel = info[1]

    def delete(self):
        db = Database()
        db.call("jdrdelete",idserv=self.server,idchan=self.channel)
        db.close()

    def MJtransfer(self,member_id):
        db = Database()
        db.call("mjtransfer",idserv=self.server,idchan=self.channel,mj=member_id)
        db.close()

    def copy(self,channel_id):
        db = Database()
        db.call("jdrcopy",idserv=self.server,src=self.channel,dest=channel_id)
        db.close()

    def charcreate(self,chardbkey,idclass):
        db = Database()
        db.call("charcreate",dbkey=chardbkey,idserv=self.server,idchan=self.channel,cl=idclass)
        db.close()

    def chardelete(self,chardbkey):
        db = Database()
        db.call("chardelete",dbkey=chardbkey,idserv=self.server,idchan=self.channel)
        db.close()

    def extend(self,channel_id):
        db = Database()
        db.call("JDRextend",idserv=self.server,src=self.channel,target=channel_id)
        db.close()

    def unextend(self,channel_id):
        db = Database()
        db.call("JDRstopextend",idserv=self.server,src=self.channel,target=channel_id)
        db.close()

    def unextend_all(self):
        db = Database()
        db.call("JDRstopallextend",idserv=self.server,src=self.channel)
        db.close()

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

    def charlist(self):
        db = Database()
        cur = db.call("get_allcharacter",idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find character")
        ls = []
        for i in cur:
            ls.append(i[0])
        db.close()
        return ls

    def get_charbase(self):
        ls = self.charlist()
        charbase = []
        for i in ls:
            charbase.append(self.get_character(i))
        return charbase

    def get_serverinfo(self):
        return DBServer(self.server)

    def set_finalizer_field(self,title,content):
        db = Database()
        db.call("set_finalize_field",idserv=self.server,idchan=self.channel,titl=title,descr=content)
        db.close()

    def del_finalizer_field(self,title):
        db = Database()
        db.call("del_finalize_field",idserv=self.server,idchan=self.channel,titl=title)
        db.close()

    def get_finalizer(self):
        db = Database()
        cur = db.call("finalizer",idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close()
            return []
        ls = []
        for i in cur:
            ls.append((i[2],i[3]))
        db.close()
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
