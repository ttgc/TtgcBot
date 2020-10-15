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
from src.utils.DatabaseManager import *
#from tools.BotTools import DBJDR
#import tools.BotTools as bt
from src.tools.CharacterUtils import *

class Character:
    """Character class"""
    lvlcolor = ["00FF00","FFFF00","FF00FF","FF0000"]
    gm_map_chartoint = {'O': 0, 'D': 1, 'I': 2, 'S': 3}
    gm_map_inttochar = ['O', 'D', 'I', 'S']
    gm_map_inttostr = ['offensive', 'defensive', 'illumination', 'sepulchral']

    def __init__(self,**kwargs):
        self.key = kwargs.get("charkey","unknown")
        self.name = kwargs.get("name","unknown")
        self.lore = kwargs.get("lore","")
        self.PVmax = kwargs.get("PVm",1)
        self.PMmax = kwargs.get("PMm",1)
        self.PV = kwargs.get("PV",1)
        self.PM = kwargs.get("PM",1)
        self.force = kwargs.get("force",50)
        self.esprit = kwargs.get("esprit",50)
        self.charisme = kwargs.get("charisme",50)
        self._furtivite = kwargs.get("furtivite",50)
        self.karma = kwargs.get("karma",0)
        self.money = kwargs.get("money",0)
        self.stat = kwargs.get("stat",[0,0,0,0,0,0,0])
        self.lp = kwargs.get("lp",0)
        self.dp = kwargs.get("dp",0)
        self.mod = kwargs.get("mod",0)
        self.default_mod = kwargs.get("default_mod",0)
        self.default_karma = kwargs.get("default_karma",0)
        self.intuition = kwargs.get("intuition",3)
        self.mental = kwargs.get("mentalhealth",100)
        self.lvl = kwargs.get("lvl",1)
        self.linked = kwargs.get("linked","NULL")
        if self.linked.upper() == "NULL": self.linked = None
        self.selected = kwargs.get("selected",False)
        self.inventory = kwargs.get("inventory",Inventory())
        self.pet = kwargs.get("pet",{})
        self.skills = kwargs.get("skills",[])
        self.dead = kwargs.get("dead",False)
        self.race,self.classe = retrieveCharacterOrigins(kwargs.get("classe",1))
        self.jdr = None
        self.xp = kwargs.get("xp",0)
        self.precision = kwargs.get("prec",50)
        self.luck = kwargs.get("luck",50)
        self.affiliated_with = kwargs.get("org",None)
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

    def bind(self,jdr):
        self.inventory.bind(self,jdr)
        self.jdr = jdr
        for i in self.pet.keys():
            self.pet[i].bind(jdr)

    def check_life(self):
        if self.PV <= 0:
            return False
        else:
            return True

    def resetchar(self):
        db = Database()
        db.call("resetchar",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
        self.karma = self.default_karma
        self.PV = self.PVmax
        self.PM = self.PMmax
        self.mod = self.default_mod

    def charset(self,tag,value):
        db = Database()
        db.call("charset",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,stat=tag,val=value)
        db.close()
        return self.jdr.get_character(self.key)

    def makehybrid(self, race, allowOverride=False):
        if allowOverride or self.hybrid_race is None:
            db = Database()
            db.call("charhybrid", dbkey=self.key, idserv=self.jdr.server, idchan=self.jdr.channel, rc=race)
            db.close()
            return self.jdr.get_character(self.key)
        return self

    def setsymbiont(self, symbiont):
        db = Database()
        db.call("charsb", dbkey=self.key, idserv=self.jdr.server, idchan=self.jdr.channel, sb=symbiont)
        db.close()
        return self.jdr.get_character(self.key)

    def setlore(self,lore):
        db = Database()
        db.call("charsetlore",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,lor=lore)
        db.close()
        self.lore = lore

    def setname(self,name_):
        db = Database()
        db.call("charsetname",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,name=name_)
        db.close()
        self.name = name_

    def switchmod(self,default=False):
        db = Database()
        db.call("switchmod",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,def_=default)
        db.close()
        return self.jdr.get_character(self.key)

    def link(self,memberid):
        db = Database()
        db.call("charlink",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,idmemb=memberid)
        db.close()
        self.linked = memberid

    def unlink(self):
        db = Database()
        db.call("charunlink",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
        self.linked = None

    def select(self):
        if self.linked is None: return
        db = Database()
        db.call("charselect",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,idmemb=self.linked)
        db.close()
        self.selected = True

    def lvlup(self):
        db = Database()
        db.call("levelup",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
        self.lvl += 1

    def uselp(self):
        db = Database()
        db.call("usepoints",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,item="lightpt")
        db.close()
        self.lp -= 1
        self.karma = 10
        self.mod = 2

    def usedp(self):
        db = Database()
        db.call("usepoints",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,item="darkpt")
        db.close()
        self.dp -= 1
        self.karma = -10
        self.mod = 3

    def reset_lpdp(self):
        db = Database()
        db.call("end_lpdp_gamemod",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()
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
        self.dead = True
        db = Database()
        db.call("kill",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel)
        db.close()

    def xpup(self,amount,allowlevelup=False):
        db = Database()
        cur = db.call("charxp",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,amount=amount,allowlevelup=allowlevelup)
        result = cur.fetchone()
        db.close()
        return result[0]

    def affiliate(self,org):
        # if self.affiliated_with is not None:
        #     raise AttributeError("Character {} is already affiliated with an (other) organization".format(self.key))
        db = Database()
        db.call("affiliate",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,org=org)
        db.close()

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
