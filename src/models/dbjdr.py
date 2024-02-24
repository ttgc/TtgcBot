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

from utils.decorators import deprecated
from datahandler.api import APIManager
from datahandler.cache import DataCache
from exceptions import APIException
from network import RequestType
from models.inventory import Inventory
from models.pet import Pet
from models.skills import Skill
from models.character import Character
from models.enums import AutoPopulatedEnums, Extension

class DBJDR:
    def __init__(self, srvid, channelid, requester, requesterRole):
        self.api = APIManager()
        self.server = srvid
        self.requester = requester
        self.requesterRole = requesterRole
        self._initialChannelID = channelid
        self.creation_date = None
        self.pjs = -1
        self.mj = self.requester
        self.channel = self._initialChannelID
        self.extensions = []

    @classmethod
    async def pull(cls, srvid, channelid, requester, requesterRole):
        jdr = cls(srvid, channelid, requester, requesterRole)
        info = await jdr.api(RequestType.GET, "JDR/{}/{}".format(jdr.server, jdr._initialChannelID),
            resource="SRV://{}/{}".format(jdr.server, jdr._initialChannelID), requesterID=jdr.requester, roleID=jdr.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Unable to find JDR", srv=jdr.server, channel=jdr._initialChannelID, code=info.status)

        jdr.creation_date = info.result.get("creation", None)
        jdr.pjs = info.result.get("players", -1)
        jdr.mj = info.result.get("owner", jdr.requester)
        jdr.channel = info.result.get("channel", jdr._initialChannelID)
        jdr.extensions = info.result.get("extensions", [])

        cache = DataCache()
        for i in [jdr.channel] + jdr.extensions:
            if i != jdr._initialChannelID:
                cache.mapitems("SRV://{}/{}".format(jdr.server, jdr._initialChannelID), "SRV://{}/{}".format(jdr.server, i))

        return jdr

    async def delete(self):
        info = await self.api(RequestType.DELETE, "JDR/delete", body={"server": self.server, "channel": self.channel},
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR delete error", srv=self.server, channel=self.channel, code=info.status)
        DataCache.remove("SRV://{}/{}".format(self.server, self._initialChannelID), True)

    async def MJtransfer(self, member_id):
        info = await self.api(RequestType.PUT, "JDR/transfer/{}/{}".format(self.server, self.channel),
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole,
            body={"master": member_id})

        if info.status // 100 != 2:
            raise APIException("MJ transfer error", srv=self.server, channel=self.channel, oldmj=self.mj, newmj=member_id, code=info.status)
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
            raise APIException("JDR copy error", srv=self.server, channel=self.channel, tochan=channel_id, code=info.status)

        copied = await DBJDR.pull(self.server, channel_id, self.requester, self.requesterRole)
        return copied

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
            raise APIException("Char create error", srv=self.server, channel=self.channel, charkey=chardbkey, code=info.status)

    async def chardelete(self, chardbkey):
        info = await self.api(RequestType.DELETE, "Character/delete/{}/{}/{}".format(self.server, self.channel, chardbkey),
            resource="SRV://{}/{}/{}".format(self.server, self._initialChannelID, chardbkey), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Char delete error", srv=self.server, channel=self.channel, charkey=chardbkey, code=info.status)

    async def extend(self, channel_id, *other_channels):
        reqbody = {
            "server": self.server,
            "from": self.channel,
            "to": [channel_id] + list(other_channels)
        }

        info = await self.api(RequestType.POST, "JDR/extend", body=reqbody,
            resource="SRV://{}/{}".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("JDR extend error", srv=self.server, channel=self.channel, code=info.status)
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
            raise APIException("JDR unextend error", srv=self.server, channel=self.channel, code=info.status)
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
            raise APIException("JDR unextend all error", srv=self.server, channel=self.channel, code=info.status)
        self.extensions = []
        DataCache().remove("SRV://{}/{}".format(self.server, self._initialChannelID), True)

    async def get_character(self, charkey, forceGet=False):
        info = await self.api(RequestType.GET, "Character/{}/{}/{}".format(self.server, self.channel, charkey), forceGet=forceGet,
            resource="SRV://{}/{}/{}".format(self.server, self._initialChannelID, charkey), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Character get error", srv=self.server, channel=self.channel, charkey=charkey, code=info.status)

        rawchar = info.result
        stat = [
            rawchar.get("RolledDice", 0), rawchar.get("SuperCriticSuccess", 0), rawchar.get("CriticSuccess", 0), rawchar.get("Succes", 0),
            rawchar.get("Fail", 0), rawchar.get("CriticFail", 0), rawchar.get("SuperCriticFail", 0)
        ]

        Gamemods = await AutoPopulatedEnums().get_gamemods()
        gm = Gamemods.from_str(rawchar.get("Gm", "offensive").lower())
        gmdefault = Gamemods.from_str(rawchar.get("GmDefault", "offensive").lower())
        inv = Inventory.char_loadfromdb(self.server, self.channel, charkey, self.requester, self.requesterRole, rawchar.get("MaxInvsize", 20))
        pets = Pet.listpet(self.server, self.channel, charkey, self.requester, self.requesterRole, api=self.api, nologin=True)
        skls = Skill.loadfromdb(self.server, self.channel, charkey, self.requester, self.requesterRole, api=self.api, nologin=True)
        ext = rawchar.get("Extension", {})
        char = Character(charkey=charkey, name=rawchar.get("Nom", charkey),
                            lvl=rawchar.get("Lvl", 1), PV=rawchar.get("Pv", 1), PVm=rawchar.get("Pvmax", 1), PM=rawchar.get("Pm", 1),
                            PMm=rawchar.get("Pmmax", 1), force=rawchar.get("Strength", 50), esprit=rawchar.get("Spirit", 50),
                            charisme=rawchar.get("Charisma", 50), furtivite=rawchar.get("Agility", 50), karma=rawchar.get("Karma", 0),
                            default_karma=rawchar.get("DefaultKarma", 0), money=rawchar.get("Argent", 0), lp=rawchar.get("LightPoints", 0),
                            dp=rawchar.get("DarkPoints", 0), intuition=rawchar.get("Intuition", 3), mentalhealth=rawchar.get("Mental", 100),
                            stat=stat, mod=gm, default_mod=gmdefault, inventory=inv,
                            linked=rawchar.get("IdMember", None), pet=pets, skills=skls, dead=rawchar.get("Dead", False),
                            race=rawchar.get("Race", "Unknown"), classe=rawchar.get("Classe", "Unknown"), selected=rawchar.get("Linked", False),
                            xp=rawchar.get("Xp", 0), prec=rawchar.get("Prec", 50), luck=rawchar.get("Luck", 50),
                            org=rawchar.get("AffiliatedWith", {}).get("Organization", None),
                            hide_org=rawchar.get("AffiliatedWith", {}).get("Hidden", False),
                            hybrid=rawchar.get("HybridRace", None), symbiont=rawchar.get("Symbiont", None),
                            planet_pilot=rawchar.get("PilotP", -1), astral_pilot=rawchar.get("PilotA", -1),
                            ext=Extension(ext.get("universe", "Cosmorigins"), ext.get("world", "Terae")))
        char.bind(self)
        return char

    async def charlist(self):
        info = await self.api(RequestType.GET, "Character/{}/{}".format(self.server, self.channel),
            resource="SRV://{}/{}".format(self.server, self.channel), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Character list error", srv=self.server, channel=self.channel, code=info.status)

        return info.result

    @deprecated("Too many API queries, avoid using this method at all cost", raise_error=False)
    async def get_charbase(self):
        chars = await self.charlist()
        ls = chars.get("characters", [])
        charbase = []
        for i in ls:
            character = await self.get_character(i)
            charbase.append(character)
        return charbase

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
            raise APIException("Finalize set error", srv=self.server, channel=self.channel, fields=fields, code=info.status)

    async def del_finalizer_field(self, *fields):
        reqbody = {
            "fields": list(fields)
        }

        info = await self.api(RequestType.DELETE, "Finalize/delete/{}/{}".format(self.server, self.channel), body=reqbody,
            resource="SRV://{}/{}/finalize".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Finalize delete error", srv=self.server, channel=self.channel, fields=fields, code=info.status)

    async def get_finalizer(self):
        info = await self.api(RequestType.GET, "Finalize/{}/{}".format(self.server, self.channel),
            resource="SRV://{}/{}/finalize".format(self.server, self._initialChannelID), requesterID=self.requester, roleID=self.requesterRole)

        if info.status // 100 != 2:
            raise APIException("Finalize set error", srv=self.server, channel=self.channel, code=info.status)

        ls = []
        for i in info.result.get("fields", []):
            ls.append((i.get("title"), i.get("content")))
        return ls
