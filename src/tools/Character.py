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
        self.furtivite = kwargs.get("furtivite",50)
        self.karma = kwargs.get("karma",0)
        self.money = kwargs.get("money",0)
        self.stat = kwargs.get("stat",[0,0,0,0,0,0,0])
        self.lp = kwargs.get("lp",0)
        self.dp = kwargs.get("dp",0)
        #self.regenkarm = [0,kwargs.get("regenkarma",None)]
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
        #mod 0 = offensiv / mod 1 = defensiv

    def __str__(self):
        return self.name

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
        self.mod = 1

    def usedp(self):
        db = Database()
        db.call("usepoints",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,item="darkpt")
        db.close()
        self.dp -= 1
        self.karma = -10
        self.mod = 0

    async def roll(self,channel,lang,stat,modifier):
        if stat == "force":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                val = -2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma -= abs(val)
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                val = 2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma += val
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.force+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["force"],str(result),str(dice),"-",str(kar),str(self.force+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.force+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["force"],str(result),str(dice),"+",str(kar),str(self.force+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        val = 1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    elif result <= 10:
                        self.stat[2] += 1
                        val = -1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result <= self.force+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["force"],str(result),str(self.force+modifier)))
    ##            self.regenkarm[0] += self.regenkarm[1]
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("hasroll",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.force+modifier,val=result)
            db.close()
        elif stat == "esprit":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                val = -2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma -= abs(val)
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                val = 2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma += val
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.esprit+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"-",str(kar),str(self.esprit+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.esprit+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"+",str(kar),str(self.esprit+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        val = 1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    elif result <= 10:
                        self.stat[2] += 1
                        val = -1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result <= self.esprit+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["esprit"],str(result),str(self.esprit+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("hasroll",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.esprit+modifier,val=result)
            db.close()
        elif stat == "charisme":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                val = -2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma -= abs(val)
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                val = 2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma += val
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.charisme+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"-",str(kar),str(self.charisme+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.charisme+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"+",str(kar),str(self.charisme+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        val = 1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    elif result <= 10:
                        self.stat[2] += 1
                        val = -1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result <= self.charisme+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["charisme"],str(result),str(self.charisme+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("hasroll",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.charisme+modifier,val=result)
            db.close()
        elif stat == "furtivite" or stat == "agilite":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                val = -2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma -= abs(val)
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                val = 2
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma += val
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.furtivite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"-",str(kar),str(self.furtivite+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        val = -2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        val = 2
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            val = 1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma += val
                        elif result <= 10:
                            self.stat[2] += 1
                            val = -1
                            if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                            if Skill.isskillin(self.skills,84): #creature harmonieuse
                                if self.karma == 0 and val < 0: val -= 5
                                elif self.karma == 0 and val > 0: val +=5
                                elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                                elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                            if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                            if self.karma+val > 10: val=10-self.karma#char.karma = 10
                            self.charset('kar',val)
                            self.karma -= abs(val)
                        elif result <= self.furtivite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"+",str(kar),str(self.furtivite+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        val = 1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma += val
                    elif result <= 10:
                        self.stat[2] += 1
                        val = -1
                        if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                        if Skill.isskillin(self.skills,84): #creature harmonieuse
                            if self.karma == 0 and val < 0: val -= 5
                            elif self.karma == 0 and val > 0: val +=5
                            elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                            elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                        if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                        if self.karma+val > 10: val=10-self.karma#char.karma = 10
                        self.charset('kar',val)
                        self.karma -= abs(val)
                    elif result <= self.furtivite+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["agilite"],str(result),str(self.furtivite+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("hasroll",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.furtivite+modifier,val=result)
            db.close()
        elif stat == "chance":
            resultc = randint(1,6)
            await channel.send(lang["result_test_nomax"].format(lang["chance"],str(resultc)))
            if resultc == 1: await channel.send(lang["chance_1"])
            elif resultc == 2: await channel.send(lang["chance_2"])
            elif resultc == 3: await channel.send(lang["chance_3"])
            elif resultc == 4: await channel.send(lang["chance_4"])
            elif resultc == 5: await channel.send(lang["chance_5"])
            elif resultc == 6: await channel.send(lang["chance_6"])
        #elif stat == "malchance":
            resultm = randint(1,6)
            await channel.send(lang["result_test_nomax"].format(lang["malchance"],str(resultm)))
            if resultm == 1: await channel.send(lang["malchance_1"])
            elif resultm == 2: await channel.send(lang["malchance_2"])
            elif resultm == 3: await channel.send(lang["malchance_3"])
            elif resultm == 4: await channel.send(lang["malchance_4"])
            elif resultm == 5: await channel.send(lang["malchance_5"])
            elif resultm == 6: await channel.send(lang["malchance_6"])
            if resultc < resultm:
                val = 1
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma += val
                if self.karma > 10: self.karma = 10
            else:
                val = -1
                if Skill.isskillin(self.skills,7): val *= 2 #chanceux
                if Skill.isskillin(self.skills,84): #creature harmonieuse
                    if self.karma == 0 and val < 0: val -= 5
                    elif self.karma == 0 and val > 0: val +=5
                    elif self.karma+val > -5 and self.karma+val < 5 and val < 0: val -= 9
                    elif self.karma+val > -5 and self.karma+val < 5 and val > 0: val += 9
                if self.karma+val < -10: val=-10-self.karma#char.karma = -10
                if self.karma+val > 10: val=10-self.karma#char.karma = 10
                self.charset('kar',val)
                self.karma -= abs(val)
                if self.karma < -10: self.karma = -10
            if resultc == resultm:
                await channel.send(lang["superchance"])
                if resultc == 1: await channel.send(lang["superchance_1"])
                elif resultc == 2: await channel.send(lang["superchance_2"])
                elif resultc == 3: await channel.send(lang["superchance_3"])
                elif resultc == 4: await channel.send(lang["superchance_4"])
                elif resultc == 5: await channel.send(lang["superchance_5"])
                elif resultc == 6: await channel.send(lang["superchance_6"])
        elif stat == "intuition" or stat == "instinct":
            result = randint(1,6)
            await channel.send(lang["result_test"].format(lang[stat],str(result),str(self.intuition+modifier)))
        if self.karma > 10: self.karma = 10
        if self.karma < -10: self.karma = -10

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
        if self.affiliated_with is not None:
            raise AttributeError("Character {} is already affiliated with an (other) organization".format(self.key))
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

    async def roll(self,channel,lang,stat,modifier):
        if stat == "force":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.force+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["force"],str(result),str(dice),"-",str(kar),str(self.force+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.force+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["force"],str(result),str(dice),"+",str(kar),str(self.force+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.petset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.petset('kar',-1)
                        self.karma -= 1
                    elif result <= self.force+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["force"],str(result),str(self.force+modifier)))
    ##            self.regenkarm[0] += self.regenkarm[1]
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("pethasroll",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.force+modifier,val=result)
            db.close()
        elif stat == "esprit":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.esprit+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"-",str(kar),str(self.esprit+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.esprit+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"+",str(kar),str(self.esprit+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.petset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.petset('kar',-1)
                        self.karma -= 1
                    elif result <= self.esprit+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["esprit"],str(result),str(self.esprit+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("pethasroll",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.esprit+modifier,val=result)
            db.close()
        elif stat == "charisme":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.charisme+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"-",str(kar),str(self.charisme+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.charisme+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"+",str(kar),str(self.charisme+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.petset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.petset('kar',-1)
                        self.karma -= 1
                    elif result <= self.charisme+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["charisme"],str(result),str(self.charisme+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("pethasroll",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.charisme+modifier,val=result)
            db.close()
        elif stat == "furtivite" or stat == "agilite":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                await channel.send(lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                await channel.send(lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.agilite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"-",str(kar),str(self.agilite+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        await channel.send(lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        await channel.send(lang["66"],tts=True)
                        self.petset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.petset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.petset('kar',-1)
                            self.karma -= 1
                        elif result <= self.agilite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        await channel.send(lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"+",str(kar),str(self.agilite+modifier)))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.petset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.petset('kar',-1)
                        self.karma -= 1
                    elif result <= self.agilite+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    await channel.send(lang["result_test"].format(lang["agilite"],str(result),str(self.agilite+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("pethasroll",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.agilite+modifier,val=result)
            db.close()
        elif stat == "intuition" or stat == "instinct":
            result = randint(1,6)
            await channel.send(lang["result_test"].format(lang[stat],str(result),str(self.instinct+modifier)))
        if self.karma > 10: self.karma = 10
        if self.karma < -10: self.karma = -10
