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
from exceptions import NotBoundException, APIException, InternalCommandError
from utils.decorators import deprecated
from models.enums import Gamemods, TagList

class Pet:
    def __init__(self, **kwargs):
        self.key = kwargs.get("petkey", "unknown")
        self.charkey = kwargs.get("charkey", "unknown")
        self.name = kwargs.get("name", "unknown")
        self.espece = kwargs.get("espece", "unknown")
        self.PVmax = kwargs.get("PVm", 1)
        self.PMmax = kwargs.get("PMm", 0)
        self.PV = kwargs.get("PV", 1)
        self.PM = kwargs.get("PM", 0)
        self.force = kwargs.get("force", 50)
        self.esprit = kwargs.get("esprit", 50)
        self.charisme = kwargs.get("charisme", 50)
        self.agilite = kwargs.get("agilite", 50)
        self.karma = kwargs.get("karma", 0)
        self.stat = kwargs.get("stat", [0, 0, 0, 0, 0, 0, 0])
        self.mod = Gamemods.from_int(kwargs.get("mod", 0))
        self.default_mod = Gamemods.from_int(kwargs.get("default_mod", 0))
        self.instinct = kwargs.get("instinct", 3)
        self.lvl = kwargs.get("lvl", 1)
        self.precision = kwargs.get("prec", 50)
        self.luck = kwargs.get("luck", 50)
        self.jdr = None

    def __str__(self):
        return self.name

    @property
    def api(self):
        return self.jdr.api if self.is_bound() else None

    def bind(self,jdr):
        self.jdr = jdr

    def is_bound(self, raise_error=False):
        bound = self.jdr is not None
        if raise_error and not bound:
            raise NotBoundException(self, "Pet is not bound to a JDR instance")
        return bound

    def check_life(self):
        return self.PV > 0

    async def _internal_petset(self, requester, **kwargs):
        info = await self.api(RequestType.PUT, "Pet/set/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.charkey, self.key),
            resource="SRV://{}/{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.charkey, self.key), requesterID=requester, body=kwargs)

        if info.status // 100 != 2:
            raise APIException("Pet set error", srv=self.jdr.server, channel=self.jdr.channel, character=self.charkey, pet=self.key, code=info.status, body=kwargs)

        return info

    async def _internal_update(self, requester, **kwargs):
        info = await self.api(RequestType.PUT, "Pet/update/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.charkey, self.key),
            resource="SRV://{}/{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.charkey, self.key), requesterID=requester, body=kwargs)

        if info.status // 100 != 2:
            raise APIException("Pet update error", srv=self.jdr.server, channel=self.jdr.channel, character=self.charkey, pet=self.key, code=info.status, body=kwargs)

        return info

    async def petset(self, tag, value, requester):
        self.is_bound(True)
        tag = tag.lower()

        if tag not in TagList.PETSET:
            raise InternalCommandError("Invalid tag for petset command")

        data = {tag: value}
        info = await self._internal_petset(requester, **data)

        if tag == "name": self.name = value
        elif tag == "pv": self.PVmax, self.PV = value, min(self.PV, value)
        elif tag == "pm": self.PMmax, self.PM = value, min(self.PM, value)
        elif tag == "strength": self.force = max(1, min(100, value))
        elif tag == "spirit": self.esprit = max(1, min(100, value))
        elif tag == "charisma": self.charisme = max(1, min(100, value))
        elif tag == "agility": self.agilite = max(1, min(100, value))
        elif tag == "precision": self.precision = max(1, min(100, value))
        elif tag == "luck": self.luck = max(1, min(100, value))
        elif tag == "instinct": self.instinct = max(1, min(6, value))
        elif tag == "gamemod": self.default_mod = Gamemods.from_charcode(value)
        elif tag == "species": self.espece = value

    async def update(self, tag, value, requester):
        self.is_bound(True)
        tag = tag.lower()

        if tag not in TagList.PETUPDATE:
            raise InternalCommandError("Invalid tag for pet update command")

        data = {tag: value}
        info = await self._internal_update(requester, **data)

        if tag == "pv": self.PV = min(self.PVmax, self.PV + value)
        elif tag == "pm": self.PM = min(self.PMmax, self.PM + value)
        elif tag == "karma": self.karma = max(-10, min(10, value))

    @deprecated("Old feature using DatabaseManager")
    def setname(self, name_):
        # db = Database()
        # db.call("petsetname",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,name=name_)
        # db.close()
        self.name = name_

    @deprecated("Old feature using DatabaseManager")
    def setespece(self, espece):
        # db = Database()
        # db.call("petsetespece",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,esp=espece)
        # db.close()
        self.espece = espece

    async def switchmod(self, requester, default=False):
        if not default and int(self.mod) > 1: return
        if default and self.mod == self.default_mod: return

        self.is_bound(True)

        if default:
            self.mod = self.default_mod
        else:
            self.mod = Gamemods.OFFENSIVE if self.mod == Gamemods.DEFENSIVE else Gamemods.DEFENSIVE

        info = await self._internal_update(requester, gamemod=str(self.mod))

    async def lvlup(self, requester):
        self.is_bound(True)

        info = await self.api(RequestType.PUT, "Pet/levelup/{}/{}/{}/{}".format(self.jdr.server, self.jdr.channel, self.charkey, self.key),
            resource="SRV://{}/{}/{}/{}".format(self.jdr.server, self.jdr._initialChannelID, self.charkey, self.key), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Pet levelup error", srv=self.jdr.server, channel=self.jdr.channel, character=self.charkey, pet=self.key, code=info.status)

        self.lvl += 1

    @classmethod
    async def loadfromdb(cl, srv, channel, charkey, petkey, requester, requesterRole, *, api=None, nologin=False):
        if api is None:
            api = APIManager()
            nologin = False

        info = await api(RequestType.GET, "Pet/{}/{}/{}/{}".format(srv, channel, charkey, petkey),
            resource="SRV://{}/{}/{}/{}".format(srv, channel, charkey, petkey), requesterID=requester, roleID=self.requesterRole, disable_autologin=nologin)

        if info.status // 100 != 2:
            raise APIException("Pet get error", srv=srv, channel=channel, character=charkey, petkey=petkey, code=info.status)

        st = [
            info.result.get("RolledDice", 0), info.result.get("SuperCriticSuccess", 0), info.result.get("CriticSuccess", 0),
            info.result.get("Succes", 0), info.result.get("Fail", 0), info.result.get("CriticFail", 0), info.result.get("SuperCriticFail", 0)
        ]

        gm = ch.Character.gm_map_chartoint[info.result.get("Gm", "offensive").lower()]
        gmdefault = ch.Character.gm_map_chartoint[info.result.get("GmDefault", "offensive").lower()]
        return cl(petkey=petkey, charkey=charkey, name=info.result.get("Nom", "unknwon"), espece=info.result.get("Species", "unknown"),
                    PVm=info.result.get("Pvmax", 1), PMm=info.result.get("Pmmax", 1), PV=info.result.get("PV", 1), PM=info.result.get("PM", 1),
                    force=info.result.get("Strength", 50), esprit=info.result.get("Spirit", 50), charisme=info.result.get("Charisma", 50),
                    agilite=info.result.get("Agilite", 50), karma=info.result.get("Karma", 0), stat=st, mod=gm, default_mod=gmdefault,
                    instinct=info.result.get("Instinct", 3), prec=info.result.get("Prec", 50), luck=info.result.get("Luck", 50))

    @staticmethod
    async def listpet(srv, channel, charkey, requester, requesterRole, *, api=None, nologin=False):
        if api is None:
            api = APIManager()
            nologin = False

        info = await api(RequestType.GET, "Pet/{}/{}/{}".format(srv, channel, charkey),
            resource="SRV://{}/{}/{}".format(srv, channel, charkey), requesterID=requester, roleID=requesterRole, disable_autologin=nologin)

        if info.status // 100 != 2:
            raise APIException("Character inventory get error", srv=srv, channel=channel, charkey=charkey, code=info.status)

        pets = {}
        for i in info.result.get("Pets", []):
            pets[i] = None

        return pets
