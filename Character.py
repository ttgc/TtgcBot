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

class Character:
    """Character class"""
    def __init__(self,dic={"name":"","lore":"","PVm":1,"PMm":1,"force":50,"esprit":50,"charisme":50,"furtivite":50,"karma":0,"money":0,"stat":[0,0,0,0,0,0,0],"lp":0,"dp":0,"regenkarm":0.1,"mod":0,"armor":0,"RM":0,"PV":1,"PM":1,"default_mod":0,"default_karma":0,"intuition":3,"mentalhealth":100}):
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
        self.mod = dic["mod"]
        self.default_mod = dic["default_mod"]
        self.default_karma = dic["default_karma"]
        self.intuition = dic["intuition"]
        self.mental = dic["mentalhealth"]
        #mod 0 = offensiv / mod 1 = defensiv

    def __str__(self):
        return self.name

    def check_life(self):
        if self.PV <= 0:
            return False
        else:
            return True

    def stock(self):
        return "<"+self.name+"|"+self.lore+"|"+str(self.PVmax)+"|"+str(self.PMmax)+"|"+str(self.force)+"|"+str(self.esprit)+"|"+str(self.charisme)+"|"+str(self.furtivite)+"|"+str(self.money)+"|"+str(self.lp)+"|"+str(self.dp)+"|"+str(self.mod)+"|"+str(self.karma)+"|"+str(self.PV)+"|"+str(self.PM)+"|"+str(self.default_mod)+"|"+str(self.default_karma)+"|"+str(self.intuition)+"|"+str(self.mental)+">"


def unstockchar(string,name):
    string = string.replace("<","")
    string = string.replace(">","")
    ls = string.split("|")
    st = convert_str_into_ls(ls[-1])
    return Character({"name":ls[0],"lore":ls[1],"PVm":int(ls[2]),"PMm":int(ls[3]),"force":int(ls[4]),"esprit":int(ls[5]),"charisme":int(ls[6]),"furtivite":int(ls[7]),"karma":int(ls[12]),"money":int(ls[8]),"stat":[0,0,0,0,0,0,0],"lp":int(ls[9]),"dp":int(ls[10]),"mod":int(ls[11]),"PV":int(ls[13]),"PM":int(ls[14]),"default_mod":int(ls[15]),"default_karma":int(ls[16]),"intuition":int(ls[17]),"mentalhealth":int(ls[18])})

@asyncio.coroutine
def roll(client,channel,char,stat,modifier):
    if stat == "force":
        char.stat[0] += 1
        dice = randint(1,100)
        kar = randint(1,10)
        result = dice
        if result == 42:
            char.stat[1] += 1
            yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
            char.karma -= 2
        elif result == 66:
            char.stat[-1] += 1
            yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
            char.karma += 2
        else:
            if char.karma >= 5:
                result -= kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.force+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (force) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.force+modifier))
            elif char.karma <= -5:
                result += kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.force+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (force) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.force+modifier))
            else:
                if result == 42: char.stat[1] += 1
                elif result == 66: char.stat[-1] += 1
                elif result >= 91:
                    char.stat[-2] += 1
                    char.karma += 1
                elif result <= 10:
                    char.stat[2] += 1
                    char.karma -= 1
                elif result <= char.force+modifier: char.stat[3] += 1
                else: char.stat[-3] += 1
                yield from client.send_message(channel,"Result of test (force) :"+str(result)+"/"+str(char.force+modifier))
    elif stat == "esprit":
        char.stat[0] += 1
        dice = randint(1,100)
        kar = randint(1,10)
        result = dice
        if result == 42:
            char.stat[1] += 1
            yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
            char.karma -= 2
        elif result == 66:
            char.stat[-1] += 1
            yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
            char.karma += 2
        else:
            if char.karma >= 5:
                result -= kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.esprit+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (esprit) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.esprit+modifier))
            elif char.karma <= -5:
                result += kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.esprit+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (esprit) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.esprit+modifier))
            else:
                if result == 42: char.stat[1] += 1
                elif result == 66: char.stat[-1] += 1
                elif result >= 91:
                    char.stat[-2] += 1
                    char.karma += 1
                elif result <= 10:
                    char.stat[2] += 1
                    char.karma -= 1
                elif result <= char.esprit+modifier: char.stat[3] += 1
                else: char.stat[-3] += 1
                yield from client.send_message(channel,"Result of test (esprit) :"+str(result)+"/"+str(char.esprit+modifier))
    elif stat == "charisme":
        char.stat[0] += 1
        dice = randint(1,100)
        kar = randint(1,10)
        result = dice
        if result == 42:
            char.stat[1] += 1
            yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
            char.karma -= 2
        elif result == 66:
            char.stat[-1] += 1
            yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
            char.karma += 2
        else:
            if char.karma >= 5:
                result -= kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.charisme+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (charisme) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.charisme+modifier))
            elif char.karma <= -5:
                result += kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.charisme+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (charisme) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.charisme+modifier))
            else:
                if result == 42: char.stat[1] += 1
                elif result == 66: char.stat[-1] += 1
                elif result >= 91:
                    char.stat[-2] += 1
                    char.karma += 1
                elif result <= 10:
                    char.stat[2] += 1
                    char.karma -= 1
                elif result <= char.charisme+modifier: char.stat[3] += 1
                else: char.stat[-3] += 1
                yield from client.send_message(channel,"Result of test (charisme) :"+str(result)+"/"+str(char.charisme+modifier))
    elif stat == "furtivite" or stat == "agilite":
        char.stat[0] += 1
        dice = randint(1,100)
        kar = randint(1,10)
        result = dice
        if result == 42:
            char.stat[1] += 1
            yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
            char.karma -= 2
        elif result == 66:
            char.stat[-1] += 1
            yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
            char.karma += 2
        else:
            if char.karma >= 5:
                result -= kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.furtivite+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (agilite) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.furtivite+modifier))
            elif char.karma <= -5:
                result += kar
                if result == 42:
                    char.stat[1] += 1
                    yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                    char.karma -= 2
                elif result == 66:
                    char.stat[-1] += 1
                    yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                    char.karma += 2
                else:
                    if result >= 91:
                        char.stat[-2] += 1
                        char.karma += 1
                    elif result <= 10:
                        char.stat[2] += 1
                        char.karma -= 1
                    elif result <= char.furtivite+modifier: char.stat[3] += 1
                    else: char.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (agilite) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.furtivite+modifier))
            else:
                if result == 42: char.stat[1] += 1
                elif result == 66: char.stat[-1] += 1
                elif result >= 91:
                    char.stat[-2] += 1
                    char.karma += 1
                elif result <= 10:
                    char.stat[2] += 1
                    char.karma -= 1
                elif result <= char.furtivite+modifier: char.stat[3] += 1
                else: char.stat[-3] += 1
                yield from client.send_message(channel,"Result of test (agilite) :"+str(result)+"/"+str(char.furtivite+modifier))
    elif stat == "chance":
        resultc = randint(1,6)
        yield from client.send_message(channel,"Result of test (chance) :"+str(resultc))
        if resultc == 1: yield from client.send_message(channel,"No effect")
        elif resultc == 2: yield from client.send_message(channel,"Free action")
        elif resultc == 3: yield from client.send_message(channel,"Positiv effect")
        elif resultc == 4: yield from client.send_message(channel,"+10%")
        elif resultc == 5: yield from client.send_message(channel,"+20%")
        elif resultc == 6: yield from client.send_message(channel,"One more action !")
    #elif stat == "malchance":
        resultm = randint(1,6)
        yield from client.send_message(channel,"Result of test (malchance) :"+str(resultm))
        if resultm == 1: yield from client.send_message(channel,"No effect")
        elif resultm == 2: yield from client.send_message(channel,"hard to act")
        elif resultm == 3: yield from client.send_message(channel,"Negativ effect")
        elif resultm == 4: yield from client.send_message(channel,"-10%")
        elif resultm == 5: yield from client.send_message(channel,"-20%")
        elif resultm == 6: yield from client.send_message(channel,"Action canceled")
        if resultc < resultm:
            char.karma += 1
            if char.karma > 10: char.karma = 10
        else:
            char.karma -= 1
            if char.karma < -10: char.karma = -10
        if resultc == resultm:
            yield from client.send_message(channel,"You have won a chance bonus !")
            if resultc == 1: yield from client.send_message(channel,"Switch battle mod just for the future action")
            elif resultc == 2: yield from client.send_message(channel,"Action cannot be avoided")
            elif resultc == 3: yield from client.send_message(channel,"Instant switch with an ally")
            elif resultc == 4: yield from client.send_message(channel,"Reroll the dice if it fail (excepted 66)")
            elif resultc == 5: yield from client.send_message(channel,"Action cant fail excepted critic and super-critic fail")
            elif resultc == 6: yield from client.send_message(channel,"Choose a chance effect and a double effect")
    elif stat == "intuition":
        result = randint(1,6)
        yield from client.send_message(channel,"Result of test (intuition) :"+str(result)+"/"+str(char.intuition+modifier))
    if char.karma > 10: char.karma = 10
    if char.karma < -10: char.karma = -10
