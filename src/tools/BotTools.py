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
from enum import Enum
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

class DBJDR:
    async def __init__(self, srvid, channelid, requester, requesterRole):
        self.api = APIManager()
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
                "pv": kwargs.get("pv", 1),
                "pm": kwargs.get("pm", 1),
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

    async def get_character(self, charkey):
        info = await self.api(RequestType.GET, "Character/{}/{}/{}".format(self.server, self.channel, charkey),
            resource="SRV://{}/{}/{}".format(self.server, self.channel, charkey), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Character get error", srv=self.ID, channel=self.channel, charkey=charkey, code=info.status)

        rawchar = info.result
        stat = [
            rawchar.get("RolledDice", 0), rawchar.get("SuperCriticSuccess", 0), rawchar.get("CriticSuccess", 0), rawchar.get("Succes", 0),
            rawchar.get("Fail", 0), rawchar.get("CriticFail", 0), rawchar.get("SuperCriticFail", 0)
        ]

        gm = ch.Character.gm_map_chartoint[rawchar.get("Gm", "offensive").lower()]
        gmdefault = ch.Character.gm_map_chartoint[rawchar.get("GmDefault", "offensive").lower()]
        inv = chutil.Inventory.char_loadfromdb(self.server, self.channel, charkey, self.requester, self.requesterRole, rawchar.get("MaxInvsize", 20))
        pets = ch.Pet.listpet(self.server, self.channel, charkey, self.requester, self.requesterRole)
        skls = chutil.Skill.loadfromdb(self.server, self.channel, charkey, self.requester, self.requesterRole)
        char = ch.Character(charkey=charkey, name=rawchar.get("Nom", charkey),
                            lvl=rawchar.get("Lvl", 1), PV=rawchar.get("Pv", 1), PVm=rawchar.get("Pvmax", 1), PM=rawchar.get("Pm", 1),
                            PMm=rawchar.get("Pmmax", 1), force=rawchar.get("Strength", 50), esprit=rawchar.get("Spirit", 50),
                            charisme=rawchar.get("Charisma", 50), furtivite=rawchar.get("Agility", 50), karma=rawchar.get("Karma", 0),
                            default_karma=rawchar.get("DefaultKarma", 0), money=rawchar.get("Argent", 0), lp=rawchar.get("LightPoints", 0),
                            dp=rawchar.get("DarkPoints", 0), intuition=rawchar.get("Intuition", 3), mentalhealth=rawchar.get("Mental", 100),
                            stat=stat, mod=gm, default_mod=gmdefault, inventory=inv,
                            linked=rawchar.get("IdMember", None), pet=pets, skills=skls, dead=rawchar.get("Dead", False),
                            classe=rawchar.get("Classe", "Unknown"), selected=rawchar.get("Linked", False), xp=rawchar.get("Xp", 0),
                            prec=rawchar.get("Prec", 50), luck=rawchar.get("Luck", 50),
                            org=rawchar.get("AffiliatedWith", {}).get("Organization", None),
                            hybrid=rawchar.get("HybridRace", None), symbiont=rawchar.get("Symbiont", None),
                            planet_pilot=rawchar.get("PilotP", -1), astral_pilot=rawchar.get("PilotA", -1))
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

class MemberPermGrantable(Enum):
    MANAGER = "manager"
    PREMIUM = "premium"

class DBMember:
    async def __init__(self, ID):
        self.ID = ID
        self.api = APIManager()
        info = await self.api(RequestType.GET, "Member/{}".format(self.ID), resource="MEMBER://{}".format(self.ID), requesterID=self.ID)

        if info.status // 100 != 2:
            raise APIException("Unable to find the requested member", member=self.ID, code=info.status)

        self.perm = info.result.get("permissions", "None")
        if self.perm == "None": self.perm = None
        self.lang = info.result.get("language", {}).get("langcode", "EN")
        self.fulllangname = info.result.get("language", {}).get("name", "English") if self.lang != "EN" else "English"
        self.blacklisted = info.result.get("blacklisted", {}).get("isBlacklisted", False)
        self.blacklistReason = info.result.get("blacklisted", {}).get("reason", "")

    def is_owner(self):
        return self.perm.lower() == "owner"

    def is_manager(self):
        return (self.perm.lower() == "manager" or self.is_owner())

    def is_premium(self):
        return self.perm is not None

    def is_blacklisted(self):
        return self.blacklisted, self.blacklistReason

    async def unblacklist(self, requester):
        if not self.is_blacklisted()[0]: return
        info = await self.api(RequestType.DELETE, "Member/{}/unblacklist".format(self.ID), resource="MEMBER://{}".format(self.ID), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Member unblacklist error", member=self.ID, code=info.status)

    @classmethod
    async def blacklist(cl, memberid, requester, reason=None):
        api = APIManager()
        info = await api(RequestType.PUT, "Member/{}/blacklist".format(memberid), resource="MEMBER://{}".format(memberid),
            requesterID=requester, body={} if reason is None else {"reason": reason})

        if info.status // 100 != 2 and info.status != 409:
            raise APIException("Member blacklist error", member=memberid, code=info.status)

        return cl(memberid)

    @staticmethod
    async def grantuser(memberid, perm, requester):
        api = APIManager()
        info = await api(RequestType.PUT, "Member/{}/grant/{}".format(memberid, perm.value), resource="MEMBER://{}".format(memberid), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Member grant error", member=memberid, perm=perm.value, code=info.status)

    @staticmethod
    async def setuserlang(memberid, lang):
        api = APIManager()
        info = await api(RequestType.PUT, "Member/{}/setlang/{}".format(memberid, lang), resource="MEMBER://{}".format(memberid), requesterID=memberid)

        if info.status // 100 != 2:
            raise APIException("Member setlang error", member=memberlang, lang=lang, code=info.status)

    @classmethod
    async def getuserlang(cl, memberid):
        try:
            mb = await cl(memberid)
            return mb.lang
        except APIException as e:
            if e["code"] != 404:
                raise e
            return "EN"
