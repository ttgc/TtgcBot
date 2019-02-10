#!usr/bin/env python3.4
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
from converter import *
from DatabaseManager import *
#from BotTools import DBJDR
#import BotTools as bt
from CharacterUtils import *

class Character:
    """Character class"""
    def __init__(self,dic={"charkey":"","name":"","lore":"","PVm":1,"PMm":1,"force":50,"esprit":50,"charisme":50,"furtivite":50,"karma":0,"money":0,"stat":[0,0,0,0,0,0,0],"lp":0,"dp":0,"regenkarm":0.1,"mod":0,"armor":0,"RM":0,"PV":1,"PM":1,"default_mod":0,"default_karma":0,"intuition":3,"mentalhealth":100,"lvl":1,"linked":None,"inventory":Inventory(),"pet":{},"skills":[],"dead":False,"classe":1}):
        self.key = dic["charkey"]
        self.name = dic["name"]
        self.lore = dic["lore"]
        self.PVmax = dic["PVm"]
        self.PMmax = dic["PMm"]
        self.PV = dic["PV"]
        self.PM = dic["PM"]
        self.force = dic["force"]
        self.esprit = dic["esprit"]
        self.charisme = dic["charisme"]
        self.furtivite = dic["furtivite"]
        self.karma = dic["karma"]
        self.money = dic["money"]
        self.stat = dic["stat"]
        self.lp = dic["lp"]
        self.dp = dic["dp"]
        #self.regenkarm = [0,dic["regenkarm"]]
        self.mod = dic["mod"]
        self.default_mod = dic["default_mod"]
        self.default_karma = dic["default_karma"]
        self.intuition = dic["intuition"]
        self.mental = dic["mentalhealth"]
        self.lvl = dic["lvl"]
        self.linked = dic["linked"]
        if self.linked.upper() == "NULL": self.linked = None
        self.inventory = dic["inventory"]
        self.pet = dic["pet"]
        self.skills = dic["skills"]
        self.dead = dic["dead"]
        self.race,self.classe = retrieveCharacterOrigins(dic["classe"])
        self.jdr = None
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

    @asyncio.coroutine
    def roll(self,client,channel,lang,stat,modifier):
        if stat == "force":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                yield from client.send_message(channel,lang["42"],tts=True)
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
                yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["force"],str(result),str(dice),"-",str(kar),str(self.force+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["force"],str(result),str(dice),"+",str(kar),str(self.force+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["force"],str(result),str(self.force+modifier)))
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
                yield from client.send_message(channel,lang["42"],tts=True)
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
                yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"-",str(kar),str(self.esprit+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"+",str(kar),str(self.esprit+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["esprit"],str(result),str(self.esprit+modifier)))
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
                yield from client.send_message(channel,lang["42"],tts=True)
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
                yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"-",str(kar),str(self.charisme+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"+",str(kar),str(self.charisme+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["charisme"],str(result),str(self.charisme+modifier)))
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
                yield from client.send_message(channel,lang["42"],tts=True)
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
                yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"-",str(kar),str(self.furtivite+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
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
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"+",str(kar),str(self.furtivite+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["agilite"],str(result),str(self.furtivite+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("hasroll",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.furtivite+modifier,val=result)
            db.close()
        elif stat == "chance":
            resultc = randint(1,6)
            yield from client.send_message(channel,lang["result_test_nomax"].format(lang["chance"],str(resultc)))
            if resultc == 1: yield from client.send_message(channel,lang["chance_1"])
            elif resultc == 2: yield from client.send_message(channel,lang["chance_2"])
            elif resultc == 3: yield from client.send_message(channel,lang["chance_3"])
            elif resultc == 4: yield from client.send_message(channel,lang["chance_4"])
            elif resultc == 5: yield from client.send_message(channel,lang["chance_5"])
            elif resultc == 6: yield from client.send_message(channel,lang["chance_6"])
        #elif stat == "malchance":
            resultm = randint(1,6)
            yield from client.send_message(channel,lang["result_test_nomax"].format(lang["malchance"],str(resultm)))
            if resultm == 1: yield from client.send_message(channel,lang["malchance_1"])
            elif resultm == 2: yield from client.send_message(channel,lang["malchance_2"])
            elif resultm == 3: yield from client.send_message(channel,lang["malchance_3"])
            elif resultm == 4: yield from client.send_message(channel,lang["malchance_4"])
            elif resultm == 5: yield from client.send_message(channel,lang["malchance_5"])
            elif resultm == 6: yield from client.send_message(channel,lang["malchance_6"])
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
                yield from client.send_message(channel,lang["superchance"])
                if resultc == 1: yield from client.send_message(channel,lang["superchance_1"])
                elif resultc == 2: yield from client.send_message(channel,lang["superchance_2"])
                elif resultc == 3: yield from client.send_message(channel,lang["superchance_3"])
                elif resultc == 4: yield from client.send_message(channel,lang["superchance_4"])
                elif resultc == 5: yield from client.send_message(channel,lang["superchance_5"])
                elif resultc == 6: yield from client.send_message(channel,lang["superchance_6"])
        elif stat == "intuition" or stat == "instinct":
            result = randint(1,6)
            yield from client.send_message(channel,lang["result_test"].format(lang[stat],str(result),str(self.intuition+modifier)))
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

class Pet:
    def __init__(self,dic={"petkey":"","charkey":"","name":"","espece":"Unknown","PVm":1,"PMm":0,"force":50,"esprit":50,"charisme":50,"agilite":50,"karma":0,"stat":[0,0,0,0,0,0,0],"mod":0,"PV":1,"PM":0,"default_mod":0,"instinct":3,"lvl":1}):
        self.key = dic["petkey"]
        self.charkey = dic["charkey"]
        self.name = dic["name"]
        self.espece = dic["espece"]
        self.PVmax = dic["PVm"]
        self.PMmax = dic["PMm"]
        self.PV = dic["PV"]
        self.PM = dic["PM"]
        self.force = dic["force"]
        self.esprit = dic["esprit"]
        self.charisme = dic["charisme"]
        self.agilite = dic["agilite"]
        self.karma = dic["karma"]
        self.stat = dic["stat"]
        self.mod = dic["mod"]
        self.default_mod = dic["default_mod"]
        self.instinct = dic["instinct"]
        self.lvl = dic["lvl"]
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

    @asyncio.coroutine
    def roll(self,client,channel,lang,stat,modifier):
        if stat == "force":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                yield from client.send_message(channel,lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["force"],str(result),str(dice),"-",str(kar),str(self.force+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["force"],str(result),str(dice),"+",str(kar),str(self.force+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["force"],str(result),str(self.force+modifier)))
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
                yield from client.send_message(channel,lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"-",str(kar),str(self.esprit+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["esprit"],str(result),str(dice),"+",str(kar),str(self.esprit+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["esprit"],str(result),str(self.esprit+modifier)))
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
                yield from client.send_message(channel,lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"-",str(kar),str(self.charisme+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["charisme"],str(result),str(dice),"+",str(kar),str(self.charisme+modifier)))
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
                    yield from client.send_message(channel,lang["result_test"].format(lang["charisme"],str(result),str(self.charisme+modifier)))
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
                yield from client.send_message(channel,lang["42"],tts=True)
                self.petset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,lang["66"],tts=True)
                self.petset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        elif result <= self.furtivite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"-",str(kar),str(self.furtivite+modifier)))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,lang["42"],tts=True)
                        self.petset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,lang["66"],tts=True)
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
                        elif result <= self.furtivite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,lang["result_test_karma"].format(lang["agilite"],str(result),str(dice),"+",str(kar),str(self.furtivite+modifier)))
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
                    elif result <= self.furtivite+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    yield from client.send_message(channel,lang["result_test"].format(lang["agilite"],str(result),str(self.furtivite+modifier)))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("pethasroll",dbkey=self.key,charact=self.charkey,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.furtivite+modifier,val=result)
            db.close()
        elif stat == "intuition" or stat == "instinct":
            result = randint(1,6)
            yield from client.send_message(channel,lang["result_test"].format(lang[stat],str(result),str(self.instinct+modifier)))
        if self.karma > 10: self.karma = 10
        if self.karma < -10: self.karma = -10
