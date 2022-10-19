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

from exceptions import NotBoundException, APIException, InternalCommandError
from utils.decorators import deprecated
from network import RequestType
from models.enums import Gamemods, TagList
from models.pet import Pet
from models.skills import Skill
from models.deprecated import retrieveRaceName, retrieveSymbiontName # TO BE REMOVED
from models.inventory import Inventory

class Character:
    """Character class"""
    # lvlcolor = ["00FF00", "FFFF00", "FF00FF", "FF0000"]

    def __init__(self, **kwargs):
        self.key = kwargs.get("charkey", "unknown")
        self.name = kwargs.get("name", "unknown")
        self.lore = kwargs.get("lore", "")
        self.PVmax = kwargs.get("PVm", 1)
        self.PMmax = kwargs.get("PMm", 1)
        self.PV = kwargs.get("PV", 1)
        self.PM = kwargs.get("PM", 1)
        self.force = kwargs.get("force", 50)
        self.esprit = kwargs.get("esprit", 50)
        self.charisme = kwargs.get("charisme", 50)
        self._furtivite = kwargs.get("furtivite", 50)
        self.karma = kwargs.get("karma", 0)
        self.money = kwargs.get("money", 0)
        self.stat = kwargs.get("stat", [0, 0, 0, 0, 0, 0, 0])
        self.lp = kwargs.get("lp", 0)
        self.dp = kwargs.get("dp", 0)
        self.mod = Gamemods.from_int(kwargs.get("mod", 0))
        self.default_mod = Gamemods.from_int(kwargs.get("default_mod", 0))
        self.default_karma = kwargs.get("default_karma", 0)
        self.intuition = kwargs.get("intuition", 3)
        self.mental = kwargs.get("mentalhealth", 100)
        self.lvl = kwargs.get("lvl", 1)
        self.linked = kwargs.get("linked", None)
        self.selected = kwargs.get("selected", False)
        self.inventory = kwargs.get("inventory", Inventory())
        self.pet = kwargs.get("pet", {})
        self.skills = kwargs.get("skills", [])
        self.dead = kwargs.get("dead", False)
        self.race = kwargs.get("race", "Unknown")
        self.classe = kwargs.get("classe", "Unknown")
        self.jdr = None
        self.xp = kwargs.get("xp", 0)
        self.precision = kwargs.get("prec", 50)
        self.luck = kwargs.get("luck", 50)
        self.affiliated_with = kwargs.get("org", None)
        self.hidden_affiliation = kwargs.get("hide_org", False)
        self.hybrid_race = retrieveRaceName(kwargs.get("hybrid", None))
        self.symbiont = retrieveSymbiontName(kwargs.get("symbiont", None))
        self.planet_pilot = kwargs.get("planet_pilot", -1)
        self.astral_pilot = kwargs.get("astral_pilot", -1)

    def __str__(self):
        return self.name

    @property
    def furtivite(self):
        return self._furtivite

    @furtivite.setter
    def furtivite(self, val):
        self._furtivite = val

    agilite = furtivite

    @property
    def api(self):
        return self.jdr.api if self.is_bound() else None

    def bind(self, jdr):
        self.inventory.bind(self, jdr)
        self.jdr = jdr

    def is_bound(self, raise_error=False):
        bound = self.jdr is not None
        if raise_error and not bound:
            raise NotBoundException(self, "Character is not bound to a JDR instance")
        return bound

    def check_life(self):
        return self.PV > 0

    async def resetchar(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/reset/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character reset error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.karma = self.default_karma
        self.PV = self.PVmax
        self.PM = self.PMmax
        self.mod = self.default_mod

    async def _internal_charset(self, requester, **kwargs):
        info = await self.api(RequestType.PUT, "Character/set/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester, body=kwargs)

        if info.status // 100 != 2:
            raise APIException("Character set error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status, body=kwargs)

        return info

    async def _internal_update(self, requester, **kwargs):
        info = await self.api(RequestType.PUT, "Character/update/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester, body=kwargs)

        if info.status // 100 != 2:
            raise APIException("Character update error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status, body=kwargs)

        return info

    async def charset(self, tag, value, requester):
        self.is_bound(True)
        tag = tag.lower()

        if tag not in TagList.CHARSET:
            raise InternalCommandError("Invalid tag for charset command")

        data = {tag: value}
        await self._internal_charset(requester, **data)

        if tag == "name": self.name = value
        elif tag == "pv": self.PVmax, self.PV = value, min(self.PV, value)
        elif tag == "pm": self.PMmax, self.PM = value, min(self.PM, value)
        elif tag == "strength": self.force = max(1, min(100, value))
        elif tag == "spirit": self.esprit = max(1, min(100, value))
        elif tag == "charisma": self.charisme = max(1, min(100, value))
        elif tag == "agility": self.agilite = max(1, min(100, value))
        elif tag == "precision": self.precision = max(1, min(100, value))
        elif tag == "luck": self.luck = max(1, min(100, value))
        elif tag == "intuition": self.intuition = max(1, min(6, value))
        elif tag == "mental": self.mental = value
        elif tag == "karma": self.default_karma = max(-10, min(10, value))
        elif tag == "gamemod": self.default_mod = Gamemods.from_str(value)
        elif tag == "money": self.money = min(0, value)
        elif tag == "pilot":
            self.astral_pilot = max(-1, value.get("astral", self.astral_pilot))
            self.planet_pilot = max(-1, value.get("planet", self.planet_pilot))

    async def update(self, tag, value, requester):
        self.is_bound(True)
        tag = tag.lower()

        if tag not in TagList.CHARUPDATE:
            raise InternalCommandError("Invalid tag for char update command")

        data = {tag: value}
        await self._internal_update(requester, **data)

        if tag == "pv": self.PV = min(self.PVmax, self.PV + value)
        elif tag == "pm": self.PM = min(self.PMmax, self.PM + value)
        elif tag == "mental": self.mental += value
        elif tag == "karma": self.karma = max(-10, min(10, value))
        elif tag == "money": self.money = self.money + value if self.money + value > 0 else self.money
        elif tag == "light_point": self.lp += max(0, value)
        elif tag == "dark_point": self.dp += max(0, value)

    async def makehybrid(self, race, requester, allowOverride=False):
        if allowOverride or self.hybrid_race is None:
            self.is_bound(True)
            await self._internal_charset(requester, hybrid=race)
            self.hybrid_race = race

    async def setsymbiont(self, symbiont, requester):
        self.is_bound(True)
        await self._internal_charset(requester, symbiont=symbiont)
        self.symbiont = symbiont

    @deprecated("Old feature using DatabaseManager")
    def setlore(self, lore):
        # db = Database()
        # db.call("charsetlore",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,lor=lore)
        # db.close()
        self.lore = lore

    @deprecated("Old feature using DatabaseManager")
    def setname(self, name_):
        # db = Database()
        # db.call("charsetname",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,name=name_)
        # db.close()
        self.name = name_

    async def switchmod(self, requester, default=False):
        if not default and int(self.mod) > 1: return
        if default and self.mod == self.default_mod: return

        self.is_bound(True)

        if default:
            self.mod = self.default_mod
        else:
            self.mod = Gamemods.OFFENSIVE if self.mod == Gamemods.DEFENSIVE else Gamemods.DEFENSIVE

        await self._internal_update(requester, gamemod=str(self.mod))

    async def link(self, memberid, requester, override=False, select=True):
        self.is_bound(True)

        body = {"member": memberid, "overriding": override, "selected": select}

        info = await self.api(RequestType.PUT, "Character/link/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester, body=body)

        if info.status == 409:
            return False

        if info.status // 100 != 2:
            raise APIException("Character link error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, memberid=memberid, code=info.status)

        self.linked = memberid
        self.selected = select
        return True

    async def unlink(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.DELETE, "Character/unlink/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character unlink error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.linked = None
        self.selected = False

    async def select(self, requester):
        if self.linked is None: return
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/select/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character select error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.selected = True

    async def lvlup(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/levelup/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character levelup error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.lvl += 1

    @deprecated("Workaround for API waiting for an upcoming version", raise_error=False)
    async def _uselpdp_dirty(self, what, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/uselpdp/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key, what),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character uselpdp error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, what=what, code=info.status)

    async def uselp(self, requester):
        await self._uselpdp_dirty("lp", requester)
        self.lp -= 1
        self.karma = 10
        self.mod = Gamemods.ILLUMINATION

    async def usedp(self, requester):
        await self._uselpdp_dirty("dp", requester)
        self.dp -= 1
        self.karma = -10
        self.mod = Gamemods.SEPULCHRAL

    @deprecated("Workaround for API waiting for an upcoming version", raise_error=False)
    async def _reset_lpdp_dirty(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/cleanlpdp/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character cleanlpdp error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

    async def reset_lpdp(self, requester):
        await self._reset_lpdp_dirty(requester)
        if self.mod.charcode in ['I', 'S']:
            self.mod = self.default_mod

    async def pet_add(self, key, requester, **body):
        if key in self.pet: return False
        self.is_bound(True)
        finalbody = {"key": key, "data": body}

        info = await self.api(RequestType.POST, "Pet/create/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key, key), requesterID=requester, body=finalbody)

        if info.status // 100 != 2:
            raise APIException("Pet create error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, petkey=key, code=info.status)

        newpet = Pet(petkey=key, name=key, charkey=self.key)
        newpet.bind(self.jdr)
        self.pet[key] = newpet
        return True

    async def pet_delete(self, key, requester):
        if key not in self.pet: return False
        self.is_bound(True)

        info = await self.api(RequestType.DELETE, "Pet/delete/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key, key),
            resource="SRV://{}/{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key, key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Pet delete error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, petkey=key, code=info.status)

        del self.pet[key]
        return True

    async def assign_skill(self, requester, *skls):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Skills/assign/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester, body={"skills": list(skls)})

        if info.status // 100 != 2:
            raise APIException("Skills assign error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, skills=skls, code=info.status)

        self.skills = Skill.loadfromdb(self.jdr.server, self.jdr.channel, self.key, self.requester, self.jdr.requesterRole, api=self.api, nologin=True)
        return True

    async def kill(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/kill/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character kill error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.dead = True

    async def xpup(self, amount, requester, allowlevelup=False, curve=None, *curveParameters):
        self.is_bound(True)
        xpdata = {"initial": amount, "curve": curve, "parameters": list(curveParameters), "earnlevel": allowlevelup}
        await self._internal_update(requester, xp=xpdata)

        if curve is None:
            self.xp += min(0, amount)
            if allowlevelup:
                levels = self.xp // 100
                self.lvl += levels
                self.xp -= (levels * 100)
            return self
        else:
            newself = await self.jdr.get_character(self.key, True)
            return newself

    async def affiliate(self, org, requester):
        self.is_bound(True)
        await self._internal_charset(requester, affiliation=org)
        self.affiliated_with = org

    async def get_pet(self, petkey):
        if petkey not in self.pet or not self.is_bound(): return None
        if self.pet[petkey] is None:
            self.pet[petkey] = await Pet.loadfromdb(self.jdr.server, self.jdr._initialChannelID, self.key, petkey, self.jdr.requester, self.jdr.requesterRole, api=self.api)
            if self.is_bound(): self.pet[petkey].bind(self.jdr)
        return self.pet[petkey]