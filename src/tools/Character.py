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
from random import randint,choice
#from src.converter import *
from src.tools.datahandler.APIManager import *
#from tools.BotTools import DBJDR
#import tools.BotTools as bt
from src.tools.CharacterUtils import *
from src.utils.exceptions import InternalCommandError

class Character:
    """Character class"""
    lvlcolor = ["00FF00", "FFFF00", "FF00FF", "FF0000"]
    gm_map_chartoint = {'offensive': 0, 'defensive': 1, 'illumination': 2, 'sepulchral': 3}
    gm_map_inttochar = ['O', 'D', 'I', 'S']
    gm_map_inttostr = ['offensive', 'defensive', 'illumination', 'sepulchral']

    def __init__(self,**kwargs):
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
        self.stat = kwargs.get("stat", [0,0,0,0,0,0,0])
        self.lp = kwargs.get("lp", 0)
        self.dp = kwargs.get("dp", 0)
        self.mod = kwargs.get("mod", 0)
        self.default_mod = kwargs.get("default_mod", 0)
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

    @property
    def api(self):
        return self.jdr.api if self.is_bound() else None

    @furtivite.setter
    def furtivite(self, val):
        self._furtivite = val

    agilite = furtivite

    def bind(self,jdr):
        self.inventory.bind(self, jdr)
        self.jdr = jdr

    def is_bound(self, raise_error=False):
        bound = self.jdr is not None
        if raise_error and not bound:
            raise InternalCommandError("Character is not bound")
        return bound

    def check_life(self):
        if self.PV <= 0:
            return False
        else:
            return True

    def resetchar(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/reset/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character reset error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.karma = self.default_karma
        self.PV = self.PVmax
        self.PM = self.PMmax
        self.mod = self.default_mod

    def _internal_charset(self, requester, **kwargs):
        info = await self.api(RequestType.PUT, "Character/set/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester, body=kwargs)

        if info.status // 100 != 2:
            raise APIException("Character set error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status, body=kwargs)

        return info

    def _internal_update(self, requester, **kwargs):
        info = await self.api(RequestType.PUT, "Character/update/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester, body=kwargs)

        if info.status // 100 != 2:
            raise APIException("Character update error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status, body=kwargs)

        return info

    def charset(self, tag, value, requester):
        self.is_bound(True)
        tag = tag.lower()

        if tag not in ["name", "pv", "pm", "strength", "spirit", "charisma", "agility", "precision", "luck",
                        "intuition", "mental", "karma", "gamemod", "money", "pilot"]:
            raise InternalCommandError("Invalid tag for charset command")

        data = {tag: value}
        info = self._internal_charset(requester, **data)

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
        elif tag == "gamemod": self.default_mod = self.gm_map_chartoint[value]
        elif tag == "money": self.money = min(0, value)
        elif tag == "pilot":
            self.astral_pilot = max(-1, value.get("astral", self.astral_pilot))
            self.planet_pilot = max(-1, value.get("planet", self.planet_pilot))

    def update(self, tag, value, requester):
        self.is_bound(True)
        tag = tag.lower()

        if tag not in ["pv", "pm", "mental", "karma", "money", "light_point", "dark_point"]:
            raise InternalCommandError("Invalid tag for char update command")

        data = {tag: value}
        info = self._internal_update(requester, **data)

        if tag == "pv": self.PV = min(self.PVmax, self.PV + value)
        elif tag == "pm": self.PM = min(self.PMmax, self.PM + value)
        elif tag == "mental": self.mental += value
        elif tag == "karma": self.karma = max(-10, min(10, value))
        elif tag == "money": self.money = self.money + value if self.money + value > 0 else self.money
        elif tag == "light_point": self.lp += max(0, value)
        elif tag == "dark_point": self.dp += max(0, value)

    def makehybrid(self, race, requester, allowOverride=False):
        if allowOverride or self.hybrid_race is None:
            self.is_bound(True)
            info = self._internal_charset(requester, hybrid=race)
            self.hybrid_race = race

    def setsymbiont(self, symbiont, requester):
        self.is_bound(True)
        info = self._internal_charset(requester, symbiont=symbiont)
        self.symbiont = symbiont

    @deprecated
    def setlore(self, lore):
        # db = Database()
        # db.call("charsetlore",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,lor=lore)
        # db.close()
        self.lore = lore

    @deprecated
    def setname(self, name_):
        # db = Database()
        # db.call("charsetname",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,name=name_)
        # db.close()
        self.name = name_

    def switchmod(self, requester, default=False):
        if not default and self.mod > 1: return
        if default and self.mod == self.default_mod: return

        self.is_bound(True)

        if default:
            self.mod = self.default_mod
        else:
            self.mod = 0 if self.mod == 1 else 1

        info = self._internal_update(requester, gamemod=self.gm_map_inttostr[self.mod])

    def link(self, memberid, requester, override=False, select=True):
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

    def unlink(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.DELETE, "Character/unlink/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character unlink error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.linked = None
        self.selected = False

    def select(self, requester):
        if self.linked is None: return
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/select/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character select error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.selected = True

    def lvlup(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/levelup/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character levelup error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.lvl += 1

    @deprecated(raise_error=False)
    def _uselpdp_dirty(self, what, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/uselpdp/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key, what),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character uselpdp error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, what=what, code=info.status)

    def uselp(self, requester):
        self._uselpdp_dirty("lp", requester)
        self.lp -= 1
        self.karma = 10
        self.mod = 2

    def usedp(self, requester):
        self._uselpdp_dirty("dp", requester)
        self.dp -= 1
        self.karma = -10
        self.mod = 3

    @deprecated(raise_error=False)
    def _reset_lpdp_dirty(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/cleanlpdp/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character cleanlpdp error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

    def reset_lpdp(self, requester):
        self._reset_lpdp_dirty(requester)
        if Character.gm_map_inttochar[self.mod] in ['I', 'S']: self.mod = self.default_mod

    def pet_add(self,key):
        if key in self.pet: return False
        db = Database()
        db.call("petcreate",dbkey=key,charact=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
        newpet = Pet()
        newpet.key = newpet.name = key
        newpet.charkey = self.key
        self.pet[key] = newpet
        return True

    def pet_delete(self,key):
        if key not in self.pet: return False
        db = Database()
        db.call("petdelete",dbkey=key,charact=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
        del(self.pet[key])
        return True

    def assign_skill(self,sk):
        for i in self.skills:
            if sk.ID == i.ID: return False
        db = Database()
        db.call("assign_skill",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,idskill=sk.ID)
        db.close()
        self.skills.append(sk)
        return True

    def kill(self):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Character/kill/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.key),
            resource="SRV://{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Character kill error", srv=self.jdr.server, channel=self.jdr.channel, character=self.key, code=info.status)

        self.dead = True

    def xpup(self, amount, requester, allowlevelup=False, curve=None, *curveParameters):
        self.is_bound(True)
        xpdata = {"initial": amount, "curve": curve, "parameters": list(curveParameters), "earnlevel": allowlevelup}
        info = self._internal_update(requester, xp=xpdata)

        if curve is None:
            self.xp += min(0, amount)
            if allowlevelup:
                levels = self.xp // 100
                self.lvl += levels
                self.xp -= (levels * 100)
            return self
        else:
            newself = self.jdr.get_character(self.key, True)
            return newself

    def affiliate(self, org, requester):
        self.is_bound(True)
        info = self._internal_charset(requester, affiliation=org)
        self.affiliated_with = org

    def get_pet(self, petkey):
        if petkey not in self.pet or self.jdr is None: return None
        if self.pet[petkey] is None:
            self.pet[petkey] = Pet.loadfromdb(self.jdr.server, self.jdr.channel, self.key, petkey, self.jdr.requester, self.jdr.requesterRole)
        return self.pet[petkey]

class Pet:
    def __init__(self,**kwargs):
        self.key = kwargs.get("petkey","unknown")
        self.charkey = kwargs.get("charkey","unknown")
        self.name = kwargs.get("name","unknown")
        self.espece = kwargs.get("espece","unknown")
        self.PVmax = kwargs.get("PVm",1)
        self.PMmax = kwargs.get("PMm",0)
        self.PV = kwargs.get("PV",1)
        self.PM = kwargs.get("PM",0)
        self.force = kwargs.get("force",50)
        self.esprit = kwargs.get("esprit",50)
        self.charisme = kwargs.get("charisme",50)
        self.agilite = kwargs.get("agilite",50)
        self.karma = kwargs.get("karma",0)
        self.stat = kwargs.get("stat",[0,0,0,0,0,0,0])
        self.mod = kwargs.get("mod",0)
        self.default_mod = kwargs.get("default_mod",0)
        self.instinct = kwargs.get("instinct",3)
        self.lvl = kwargs.get("lvl",1)
        self.precision = kwargs.get("prec",50)
        self.luck = kwargs.get("luck",50)
        self.jdr = None

    def __str__(self):
        return self.name

    def bind(self,jdr):
        self.jdr = jdr

    def check_life(self):
        return self.PV > 0

    def petset(self,tag,value):
        db = Database()
        db.call("petset",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,stat=tag,val=value)
        db.close()
        return self.jdr.get_character(self.charkey)

    def setname(self,name_):
        db = Database()
        db.call("petsetname",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,name=name_)
        db.close()
        self.name = name_

    def setespece(self,espece):
        db = Database()
        db.call("petsetespece",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,esp=espece)
        db.close()
        self.espece = espece

    def switchmod(self,default=False):
        db = Database()
        db.call("petswitchmod",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,def_=default)
        db.close()
        return self.jdr.get_character(self.charkey)

    def lvlup(self):
        db = Database()
        db.call("petlevelup",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
        self.lvl += 1

    @classmethod
    async def loadfromdb(cl, srv, channel, charkey, petkey, requester, requesterRole):
        pass

    @staticmethod
    async def listpet(srv, channel, charkey, requester, requesterRole):
        api = APIManager()
        info = await api(RequestType.GET, "Pet/{}/{}/{}".format(srv, channel, charkey),
            resource="SRV://{}/{}/{}".format(srv, channel, charkey), requesterID=requester, roleID=requesterRole)

        if info.status // 100 != 2:
            raise APIException("Character inventory get error", srv=srv, channel=channel, charkey=charkey, code=info.status)

        pets = {}
        for i in info.result.get("Pets", []):
            pets[i] = None
        return pets
