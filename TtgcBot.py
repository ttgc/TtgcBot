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
from threading import Thread
from INIfiles import *
from logfile import *
from PythonBDD import *
import logging
import time
from EventManager import *
import os
import zipfile
import sys
import requests

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

global TOKEN
TOKEN = ''

global file
global sex
sex = False
global logf
global ideas
ideas = {}
global statut
statut = discord.Game(name="Ohayo !")
global events
events = []
global vocal
vocal = False
global vocalco
global song
song = None
global mobs
mobs = []
global anoncer_isready
anoncer_isready = True

def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance():
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie()
        return instances[classe_definie]
    return get_instance

class Character:
    def __init__(self,dic={"name":"","lore":"","PVm":1,"PMm":1,"force":50,"esprit":50,"charisme":50,"furtivite":50,"karma":0,"money":0,"stat":[0,0,0,0,0,0,0],"lp":0,"dp":0,"regenkarm":0.1,"mod":0,"armor":0,"RM":0,"PV":1,"PM":1}):
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
        self.regenkarm = [0,dic["regenkarm"]]
        self.mod = dic["mod"]
        #mod 0 = offensiv / mod 1 = defensiv

    def __str__(self):
        return self.name

    def check_life(self):
        if self.PV <= 0:
            return False
        else:
            return True

    def stock(self):
        return "<"+self.name+"|"+self.lore+"|"+str(self.PVmax)+"|"+str(self.PMmax)+"|"+str(self.force)+"|"+str(self.esprit)+"|"+str(self.charisme)+"|"+str(self.furtivite)+"|"+str(self.money)+"|"+str(self.lp)+"|"+str(self.dp)+"|"+str(self.regenkarm[1])+"|"+str(self.mod)+"|"+str(self.karma)+"|"+str(self.PV)+"|"+str(self.PM)+">"

    def damage_inflict(self,roll,flat,dice,magic=False,allowcrit=True):
        dmg = 0
        if roll == 42 or roll == 66:
            dmg = (flat+dice)*2.5
            if self.mod == 0: dmg *= 2
        elif (magic and roll <= self.esprit and roll != 66):
            dmg = flat+randint(1,dice)
            if allowcrit and roll <= 10: dmg *= 2
            if self.mod == 0: dmg *= 2
            if dmg < 0: dmg = 0
        elif (not magic and roll <= self.force and roll != 66):
            dmg = flat+randint(1,dice)
            if allowcrit and roll <= 10: dmg *= 2
            if self.mod == 0: dmg *= 2
            if dmg < 0: dmg = 0
        elif roll >= 91:
            dmg = flat+randint(1,dice)
            dmg *= 2
            if self.mod == 0: dmg *= 2
            if dmg < 0: dmg = 0
        return dmg

def unstockchar(string,name):
    string = string.replace("<","")
    string = string.replace(">","")
    ls = string.split("|")
    st = convert_str_into_ls(ls[-1])
    return Character({"name":ls[0],"lore":ls[1],"PVm":int(ls[2]),"PMm":int(ls[3]),"force":int(ls[4]),"esprit":int(ls[5]),"charisme":int(ls[6]),"furtivite":int(ls[7]),"karma":int(ls[13]),"money":int(ls[8]),"stat":[0,0,0,0,0,0,0],"lp":int(ls[9]),"dp":int(ls[10]),"regenkarm":float(ls[11]),"mod":int(ls[12]),"PV":int(ls[14]),"PM":int(ls[15])})

def convert_str_into_dic(string):
    if string == "{}": return {}
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
    #string = string.replace(" ","")
    ls = string.split(", ")
    dic = {}
    for i in range(len(ls)):
        temp = ls[i].split(": ")
        dic[temp[0]] = temp[1]
    return dic

def convert_str_into_ls(string):
    if string == "[]": return []
    string = string.replace("[","")
    string = string.replace("]","")
    string = string.replace("'","")
    ls = string.split(", ")
    return ls

def convert_str_into_ls_spe(string):
    if string == "{}": return []
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
    ls = string.split(", ")
    return ls

def sum_ls(ls1,ls2):
    lsf = ls1[:]
    for i in range(len(lsf)):
        lsf[i] += ls2[i]
    return lsf

def get_prefix(ID):
    ID = str(ID)
    cfg = BDD("config")
    cfg.load()
    return cfg["prefix",ID]

def set_prefix(ID,new):
    ID = str(ID)
    cfg = BDD("config")
    cfg.load()
    cfg["prefix",ID] = new
    cfg.save()

def is_blacklisted(ID):
    ID = str(ID)
    bl = BDD("userlist")
    bl.load()
    black = True
    try:
        reason = bl["blacklist",ID]
    except:
        black = False
        reason = ""
    return black,reason

def is_botmanager(ID):
    ID = str(ID)
    ul = BDD("userlist")
    ul.load()
    try:
        get = ul["botmanager",ID]
    except:
        return False
    return True

def is_premium(ID):
    ID = str(ID)
    ul = BDD("userlist")
    ul.load()
    try:
        get = ul["premium",ID]
    except:
        return False
    return True

def get_charbase(ID):
    ID = str(ID)
    charbdd = BDD("character")
    charbdd.load()
    dic = convert_str_into_dic(charbdd["charbase",ID])
    if dic == {}: pass
    else:
        for i,k in dic.items():
            dic[i] = unstockchar(k,i)
    linked = convert_str_into_dic(charbdd["charlink",ID])
    for i,k in dic.items():
        k.stat = convert_str_into_ls_spe(charbdd["charstat",str(i)])
        for j in range(len(k.stat)):
            k.stat[j] = int(k.stat[j])
    return dic,linked

def save_data(ID,charbase,linked):
    ID = str(ID)
    charbdd = BDD("character")
    charbdd.load()
    dic = {}
    for i,k in charbase.items():
        dic[i] = k.stock()
    charbdd["charbase",ID] = dic
    charbdd["charlink",ID] = str(linked)
    for i,k in charbase.items():
        temp = str(k.stat)
        temp = temp.replace("[","{")
        temp = temp.replace("]","}")
        charbdd["charstat",str(i)] = temp
    charbdd.save()

client = discord.Client()

@client.event
@asyncio.coroutine
def on_message(message):
    global TOKEN
    global file,sex,logf,ideas,statut,events,vocal,vocalco,song,mobs,anoncer_isready
    logf.restart()
    #exclusion
    if message.server is None: return
    if message.author.bot: return
    #get prefix
    if message.server is not None: prefix = get_prefix(message.server.id)
    else: prefix = '/'
    #blacklisting
    blacklisted, reason = is_blacklisted(message.author.id)
    if blacklisted:
        if message.content.startswith(prefix):
            yield from client.send_message(message.channel,"I'm sorry but "+message.author.mention+" is currently blacklisted")
        return
    #message check
    if not message.content.startswith(prefix):
        conf = BDD("config")
        conf.load()
        try:
            filtre = convert_str_into_ls_spe(conf["contentban",str(message.server.id)])
        except KeyError:
            filtre = []
        for i in filtre:
            if i in message.content:
                yield from client.delete_message(message)
                yield from client.send_message(message.author,"Your message contain some banned content on this server, so it was deleted")
                return
    #special values
    premium = False
    jdrchannel = False
    admin = False
    botowner = False
    nsfw = False
    musicchannel = False
    botmanager = is_botmanager(message.author.id)
    premium = is_premium(message.author.id)
    if botmanager: premium = True
    if str(message.author.id) == "222026592896024576":
        botowner = botmanager = premium = admin = True
    if message.server != None:
        if message.author == message.server.owner: admin = True
    if message.channel.id == "328551345177231360": jdrchannel = True
    if message.channel.name.startswith("nsfw-"): nsfw = True
    else:
        head = {'Authorization': "Bot "+TOKEN}
        r = requests.get("https://discordapp.com/api/v7/channels/"+str(message.channel.id),headers=head)
        nsfw = r.json()['nsfw']
    if message.channel.id == "237668457963847681": musicchannel = True
    #get charbase
    charbase,linked = get_charbase(message.server.id)
    char = None
    if str(message.author.id) in linked:
        char = charbase[linked[str(message.author.id)]]
    #commands
    #########REWRITTEN##########
    if message.content.startswith(prefix+'setprefix') and admin:
        prefix = (message.content).replace(prefix+'setprefix ',"")
        set_prefix(message.server.id,prefix)
        logf.append("/setprefix","Changing command prefix into : "+prefix)
        yield from client.send_message(message.channel,"Changing command prefix into : "+prefix)
    if message.content.startswith(prefix+'rollindep'):
        val = message.content
        val = int(val.replace(prefix+"rollindep ",""))
        result = randint(1,val)
        yield from client.send_message(message.channel,"Result of rolling dice : "+str(result)+"/"+str(val))
    #####NOT YET REWRITTEN######
    #jdr commands
    if message.content.startswith(prefix+'roll') and jdrchannel:
        field = (message.content).replace(prefix+'roll ',"")
        while " " in field: field = field.replace(" ","")
        if "-" in field:
            msg = field.split("-")[0]
            modifier = -int(field.split("-")[1])
        elif "+" in field:
            msg = field.split("+")[0]
            modifier = int(field.split("+")[1])
        else:
            msg = field
            modifier = 0
        if msg == "force":
            char.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                char.stat[1] += 1
                yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                char.karma -= 2
            elif result == 66:
                char.stat[-1] += 1
                yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
                char.karma += 2
            else:
                if char.karma >= 5:
                    result -= kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (force) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.force+modifier))
                elif char.karma <= -5:
                    result += kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (force) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.force+modifier))
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
                    yield from client.send_message(message.channel,"Result of test (force) :"+str(result)+"/"+str(char.force+modifier))
            char.regenkarm[0] += char.regenkarm[1]
            if char.regenkarm[0] >= 1:
                if char.karma < 0: char.karma += 1
                elif char.karma > 0: char.karma -= 1
                char.regenkarm[0] -= 1
        elif msg == "esprit":
            char.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                char.stat[1] += 1
                yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                char.karma -= 2
            elif result == 66:
                char.stat[-1] += 1
                yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
                char.karma += 2
            else:
                if char.karma >= 5:
                    result -= kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (esprit) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.esprit+modifier))
                elif char.karma <= -5:
                    result += kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (esprit) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.esprit+modifier))
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
                    yield from client.send_message(message.channel,"Result of test (esprit) :"+str(result)+"/"+str(char.esprit+modifier))
            if char.regenkarm[0] >= 1:
                if char.karma < 0: char.karma += 1
                elif char.karma > 0: char.karma -= 1
                char.regenkarm[0] -= 1
        elif msg == "charisme":
            char.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                char.stat[1] += 1
                yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                char.karma -= 2
            elif result == 66:
                char.stat[-1] += 1
                yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
                char.karma += 2
            else:
                if char.karma >= 5:
                    result -= kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (charisme) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.charisme+modifier))
                elif char.karma <= -5:
                    result += kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (charisme) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.charisme+modifier))
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
                    yield from client.send_message(message.channel,"Result of test (charisme) :"+str(result)+"/"+str(char.charisme+modifier))
            if char.regenkarm[0] >= 1:
                if char.karma < 0: char.karma += 1
                elif char.karma > 0: char.karma -= 1
                char.regenkarm[0] -= 1
        elif msg == "furtivite":
            char.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                char.stat[1] += 1
                yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                char.karma -= 2
            elif result == 66:
                char.stat[-1] += 1
                yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
                char.karma += 2
            else:
                if char.karma >= 5:
                    result -= kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (furtivite) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(char.furtivite+modifier))
                elif char.karma <= -5:
                    result += kar
                    if result == 42:
                        char.stat[1] += 1
                        yield from client.send_message(message.channel,"God damn it ! You scored a 42 !!!",tts=True)
                        char.karma -= 2
                    elif result == 66:
                        char.stat[-1] += 1
                        yield from client.send_message(message.channel,"Oh Shit ! That's also called a 66",tts=True)
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
                        yield from client.send_message(message.channel,"Result of test (furtivite) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(char.furtivite+modifier))
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
                    yield from client.send_message(message.channel,"Result of test (furtivite) :"+str(result)+"/"+str(char.furtivite+modifier))
            if char.regenkarm[0] >= 1:
                if char.karma < 0: char.karma += 1
                elif char.karma > 0: char.karma -= 1
                char.regenkarm[0] -= 1
        elif msg == "chance":
            result = randint(1,6)
            yield from client.send_message(message.channel,"Result of test (chance) :"+str(result))
            if result == 1: yield from client.send_message(message.channel,"No effect")
            elif result == 2: yield from client.send_message(message.channel,"Free action")
            elif result == 3: yield from client.send_message(message.channel,"Positiv effect")
            elif result == 4: yield from client.send_message(message.channel,"One more action !")
            elif result == 5: yield from client.send_message(message.channel,"+10%")
            elif result == 6: yield from client.send_message(message.channel,"+20%")
        elif msg == "malchance":
            result = randint(1,6)
            yield from client.send_message(message.channel,"Result of test (malchance) :"+str(result))
            if result == 1: yield from client.send_message(message.channel,"No effect")
            elif result == 2: yield from client.send_message(message.channel,"hard to act")
            elif result == 3: yield from client.send_message(message.channel,"Negativ effect")
            elif result == 4: yield from client.send_message(message.channel,"Action canceled")
            elif result == 5: yield from client.send_message(message.channel,"-10%")
            elif result == 6: yield from client.send_message(message.channel,"-20%")
        elif msg == "intuition":
            result = randint(1,6)
            yield from client.send_message(message.channel,"Result of test (intuition) :"+str(result))
        if char.karma > 10: char.karma = 10
        if char.karma < -10: char.karma = -10
    if message.content.startswith(prefix+'charcreate') and premium:
        name = (message.content).replace(prefix+'charcreate ',"")
        if name in charbase:
            yield from client.send_message(message.channel,"This Character already exists use `charselect` to select it and edit it")
            return
        char = Character()
        charbase[name] = char
        yield from client.send_message(message.channel,"Creating new character called : "+name)
    if message.content.startswith(prefix+'chardelete') and admin and premium:
        name = (message.content).replace(prefix+'chardelete ',"")
        yield from client.send_message(message.channel,"Please confirm that you want to delete `"+name+"` by typing `confirm`\nthis cannot be undone !")
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,content="confirm",channel=message.channel)
        if confirm is None:
            yield from client.send_message(message.channel,"Action timeout")
            return
        del(charbase[name])
        yield from client.send_message(message.channel,"Character deleted")
    if message.content.startswith(prefix+'link') and premium:
        msg = (message.content).replace(prefix+'link ',"")
        name = msg.split(" ")[0]
        if not name in charbase:
            yield from client.send_message(message.channel,"Unexisting character")
            return
        linked[str(message.mentions[0].id)] = name
        yield from client.send_message(message.channel,"Character "+charbase[name].name+" has been succesful linked to "+message.mentions[0].mention)
    if message.content.startswith(prefix+'unlink') and premium:
        if len(message.mentions) == 0:
            del(linked[str(message.author.id)])
        else:
            del(linked[str(message.mentions[0].id)])
    if message.content.startswith(prefix+'charset') and premium:
        char = charbase[message.content.split(" ")[2]]
        if message.content.startswith(prefix+'charset name'):
            ls = (message.content).split(" ")
            for i in range(3):
                del(ls[0])
            nm = ""
            for i in ls:
                nm += i
                nm += " "
            char.name = nm[:-1]#replace(prefix+'charset name ',"")
            yield from client.send_message(message.channel,"Changing name of character successful")
        elif message.content.startswith(prefix+'charset PV'):
            char.PVmax = int((message.content).split(" ")[3])#replace(prefix+'charset PV ',""))
            yield from client.send_message(message.channel,"Changing PV max of character successful")
        elif message.content.startswith(prefix+'charset PM'):
            char.PMmax = int((message.content).split(" ")[3])#replace(prefix+'charset PM ',""))
            yield from client.send_message(message.channel,"Changing PM max of character successful")
        elif message.content.startswith(prefix+'charset force'):
            char.force = int((message.content).split(" ")[3])#replace(prefix+'charset force ',""))
            yield from client.send_message(message.channel,"Changing force of character successful")
        elif message.content.startswith(prefix+'charset esprit'):
            char.esprit = int((message.content).split(" ")[3])#replace(prefix+'charset esprit ',""))
            yield from client.send_message(message.channel,"Changing esprit of character successful")
        elif message.content.startswith(prefix+'charset charisme'):
            char.charisme = int((message.content).split(" ")[3])#replace(prefix+'charset charisme ',""))
            yield from client.send_message(message.channel,"Changing charisme of character successful")
        elif message.content.startswith(prefix+'charset furtivite'):
            char.furtivite = int((message.content).split(" ")[3])#replace(prefix+'charset furtivite ',""))
            yield from client.send_message(message.channel,"Changing furtivite of character successful")
        elif message.content.startswith(prefix+'charset lp'):
            char.lp += int((message.content).split(" ")[3])#replace(prefix+'charset lp ',""))
            if char.lp < 0: char.lp = 0
            yield from client.send_message(message.channel,"Changing Light Points of character successful")
        elif message.content.startswith(prefix+'charset dp'):
            char.dp += int((message.content).split(" ")[3])#replace(prefix+'charset dp ',""))
            if char.dp < 0: char.dp = 0
            yield from client.send_message(message.channel,"Changing Dark Points of character successful")
    if message.content.startswith(prefix+'chardmg') and premium:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'chardmg ',""))
        char.PV -= val
        yield from client.send_message(message.channel,"Character "+char.name+" has lost "+str(val)+" PV")
        yield from client.send_message(message.channel,"Remaining PV : "+str(char.PV))
        if not char.check_life():
            yield from client.send_message(message.channel,"Character "+char.name+" is dead !")
            f = open("you are dead.png","rb")
            yield from client.send_file(message.channel,f)
            f.close()
        playeffect = 0
        for i in charbase.values():
            if not i.check_life():
                playeffect += 1
    if message.content.startswith(prefix+'globaldmg') and premium:
        val = int((message.content).replace(prefix+'globaldmg ',""))
        playeffect = 0
        for i in charbase.values():
            i.PV -= val
            yield from client.send_message(message.channel,"Character "+i.name+" has lost "+str(val)+" PV")
            yield from client.send_message(message.channel,"Remaining PV : "+str(i.PV))
            if not i.check_life():
                yield from client.send_message(message.channel,"Character "+i.name+" is dead !")
                playeffect += 1
                f = open("you are dead.png","rb")
                yield from client.send_file(message.channel,f)
                f.close()
    if message.content.startswith(prefix+'charheal') and premium:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'charheal ',""))
        char.PV += val
        if char.PV > char.PVmax: char.PV = char.PVmax
        yield from client.send_message(message.channel,"Character "+char.name+" has been healed from "+str(val)+" PV")
        yield from client.send_message(message.channel,"Remaining PV : "+str(char.PV))
    if message.content.startswith(prefix+'getPM') and premium:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'getPM ',""))
        if char.PM + val < 0:
            yield from client.send_message(message.channel,"No more PM !")
        else:
            if val < 0 or admin:
                char.PM += val
                if char.PM > char.PMmax: char.PM = char.PMmax
        yield from client.send_message(message.channel,"Remaining PM of character "+char.name+" : "+str(char.PM))
    if message.content.startswith(prefix+'setkarma') and premium:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'setkarma ',""))
        char.karma += val
        if char.karma < -10: char.karma = -10
        if char.karma > 10: char.karma = 10
        yield from client.send_message(message.channel,"Karma of "+char.name+" has currently a value of :"+str(char.karma))
    if message.content.startswith(prefix+'resetchar') and premium:
        char = charbase[message.content.split(" ")[1]]
        char.PV = char.PVmax
        char.PM = char.PMmax
        char.karma = 0
        yield from client.send_message(message.channel,"Character has been reset")
    if message.content.startswith(prefix+'pay') and jdrchannel:
        val = int((message.content).replace(prefix+'pay ',""))
        if char.money-val < 0:
            yield from client.send_message(message.channel,"No more money to pay !")
        else:
            if val > 0:
                char.money -= val
        yield from client.send_message(message.channel,"Remaining Money to "+char.name+" : "+str(char.money))
    if message.content.startswith(prefix+'earnmoney') and premium:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'earnmoney ',""))
        char.money += val
        yield from client.send_message(message.channel,"Remaining Money to "+char.name+" : "+str(char.money))
    if message.content.startswith(prefix+'charinfo') and jdrchannel:
        if char.mod == 0: modd = "Offensiv"
        else: modd = "Defensiv"
        embd = discord.Embed(title=char.name,description=char.lore,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        #embd.set_image(url=message.author.avatar_url)
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name="PV :",value=str(char.PV)+"/"+str(char.PVmax),inline=True)
        embd.add_field(name="PM :",value=str(char.PM)+"/"+str(char.PMmax),inline=True)
        embd.add_field(name="Force :",value=str(char.force),inline=True)
        embd.add_field(name="Esprit :",value=str(char.esprit),inline=True)
        embd.add_field(name="Charisme :",value=str(char.charisme),inline=True)
        embd.add_field(name="Furtivite :",value=str(char.furtivite),inline=True)
        embd.add_field(name="Karma :",value=str(char.karma),inline=True)
        embd.add_field(name="Money :",value=str(char.money),inline=True)
        embd.add_field(name="Light Points :",value=str(char.lp),inline=True)
        embd.add_field(name="Dark Points :",value=str(char.dp),inline=True)
        embd.add_field(name="Mod :",value=modd,inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'map') and premium:
        f = open("mapmonde.png","rb")
        yield from client.send_file(message.channel,f)
        f.close()
    if message.content.startswith(prefix+'stat') and jdrchannel:
        embd = discord.Embed(title="Stat of Character",description=char.name,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        #embd.set_image(url=message.author.avatar_url)
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name="Dice rolled :",value=str(char.stat[0]),inline=True)
        embd.add_field(name="Super Critic Success :",value=str(char.stat[1]),inline=True)
        embd.add_field(name="Critic Success :",value=str(char.stat[2]),inline=True)
        embd.add_field(name="Success (without critic and super critic) :",value=str(char.stat[3]),inline=True)
        embd.add_field(name="Fail (without critic and super critic) :",value=str(char.stat[4]),inline=True)
        embd.add_field(name="Critic Fail :",value=str(char.stat[5]),inline=True)
        embd.add_field(name="Super Critic Fail :",value=str(char.stat[6]),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'globalstat') and jdrchannel:
        ls = [0,0,0,0,0,0,0]
        for i in charbase.values():
            ls = sum_ls(ls,i.stat)
        embd = discord.Embed(title="Stat of Character",description="all character (global stat)",colour=discord.Color(randint(0,int('ffffff',16))))
        embd.set_footer(text="The Tale of Great Cosmos")
        #embd.set_image(url=message.author.avatar_url)
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name="Dice rolled :",value=str(ls[0]),inline=True)
        embd.add_field(name="Super Critic Success :",value=str(ls[1]),inline=True)
        embd.add_field(name="Critic Success :",value=str(ls[2]),inline=True)
        embd.add_field(name="Success (without critic and super critic) :",value=str(ls[3]),inline=True)
        embd.add_field(name="Fail (without critic and super critic) :",value=str(ls[4]),inline=True)
        embd.add_field(name="Critic Fail :",value=str(ls[5]),inline=True)
        embd.add_field(name="Super Critic Fail :",value=str(ls[6]),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'use') and jdrchannel:
        if message.content.startswith(prefix+'use lightpt'):
            if char.lp <= 0:
                yield from client.send_message(message.channel,"No more Light Points")
            else:
                yield from client.send_message(message.channel,char.name+" Has used a Light Point !")
                char.lp -= 1
                char.mod = 1
                char.karma = 10
                result = randint(1,6)
                yield from client.send_message(message.channel,"Result of test (chance) :"+str(result))
                if result == 1: yield from client.send_message(message.channel,"No effect")
                elif result == 2: yield from client.send_message(message.channel,"Free action")
                elif result == 3: yield from client.send_message(message.channel,"Positiv effect")
                elif result == 4: yield from client.send_message(message.channel,"No effect")
                elif result == 5: yield from client.send_message(message.channel,"+10%")
                elif result == 6: yield from client.send_message(message.channel,"+20%")
        if message.content.startswith(prefix+'use darkpt'):
            if char.dp <= 0:
                yield from client.send_message(message.channel,"No more Dark Points")
            else:
                yield from client.send_message(message.channel,char.name+" Has used a Dark Point !")
                char.dp -= 1
                char.mod = 0
                char.karma= -10
                result = randint(1,6)
                yield from client.send_message(message.channel,"Result of test (malchance) :"+str(result))
                if result == 1: yield from client.send_message(message.channel,"No effect")
                elif result == 2: yield from client.send_message(message.channel,"hard to act")
                elif result == 3: yield from client.send_message(message.channel,"Negativ effect")
                elif result == 4: yield from client.send_message(message.channel,"No effect")
                elif result == 5: yield from client.send_message(message.channel,"-10%")
                elif result == 6: yield from client.send_message(message.channel,"-20%")
    if message.content.startswith(prefix+'switchmod') and jdrchannel:
        if char.mod == 0:
            char.mod = 1
            yield from client.send_message(message.channel,char.name+" is now on Defensiv mod !")
        else:
            char.mod = 0
            yield from client.send_message(message.channel,char.name+" is now on Offensiv mod !")
    if message.content.startswith(prefix+'mj') and jdrchannel and premium:
        if message.content.startswith(prefix+'mjcharinfo'):
            pass
    #Other commands (not JDR)
    if message.content.startswith(prefix+'tell'):
        msg = (message.content).replace(prefix+'tell ',"")
        print(str(message.author)+" : "+msg)
        logf.append("/tell",str(message.author)+" : "+msg)
        yield from client.delete_message(message)
        yield from client.send_message(message.channel,msg)
    if message.content.startswith(prefix+'ttstell'):
        msg = (message.content).replace(prefix+'ttstell ',"")
        print(str(message.author)+" : "+msg)
        logf.append("/ttstell",str(message.author)+" : "+msg)
        yield from client.delete_message(message)
        yield from client.send_message(message.channel,msg,tts=True)
    if message.content.startswith(prefix+'pi'):
        yield from client.send_message(message.channel,"3,141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 105 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 0679...\nhttp://www.nombrepi.com/")
    if message.content.startswith(prefix+'joke'):
        yield from client.send_message(message.channel,choice(["Pourquoi les japonais n'ont ils pas de chevaux ?\nParce qu'ils sont déjà poney (des japonais)",
                                                     "Pourquoi x^2 ressort-il de la foret en x ?\nParce qu'il s'est pris une racine !",
                                                     "Pourquoi 0 perd-il tous ses débats ?\nParce qu'il n'a pas d'argument !",
                                                     "Un proton dit a un electron : 'courage deprime pas ! Reste positif !",
                                                     "C'est une grenouille qui croyait qu'il était tôt mais en fait il était tard",
                                                     "Newton, Einstein et Pascal jouent à cache-cache\nEinstein commence à compter, Pascal part en courant se cacher \nNewton lui reste à coté d'Einstein et dessine un carré de 1 m de côté au sol et se place dedans\nEinstein se retourne et fait : 'Newton trouvé'\nCe à quoi Newton répond : 'non t'as trouvé 1 Newton sur 1 mètre carré, t'as trouvé 1 Pascal'",
                                                     "Heisenberg ,Schrodinger et Ohm sont dans une voiture quand ils sont stoppé par un agent de police. L’agent demande : « Savez-vous à quel vitesse vous roulez? » Heisenberg répond : « Non, mais je peux vous dire exactement où j’étais. »« Vous rouliez 20km/h au dessus de la limite ! »« Maintenant je suis perdu. »  L’agent pense qu’il y a lieu de faire une fouille et examine le coffre arrière et y découvre un chat mort. Il s’exclame : « Saviez-vous que vous avez un chat mort dans le coffre arrière. » Schrodinger répond : « Maintenant, je le sais! » L'agent décide de les arréter mais Ohm résiste.",
                                                     "Pourquoi les équations ont-elles le sens de l'humour?\nparce qu'elles ont du second degré!",
                                                     "Que dit-on d'une étudiante en lettres qui prépare son doctorat ?\nElle part en thèse (parenthèse)"
                                                     "-"]))

    if message.content.startswith(prefix+'nsfwjoke') and nsfw:
        yield from client.send_message(message.channel,choice(["Une mère tente d'ecouter au travers d'une porte ce que font ses 3 filles qui viennent de ramener chacune un petit ami pour la première fois.\nLa première rigole, la mère entre et voyant les deux au pieux demande pourquoi elle rigole, ce a quoi la première lui repond : 'une petite queue dans un grand trou ça chatouille !'\nLa seconde crie de douleur, la mère entre et demande pourquoi : 'Une grosse queue dans un petit trou ça fait mal'\nEnfin la mere n'entends rien venant de la troisième chambre, elle entre et vois sa fille en train de faire une pipe, et lui demande pourquoi on ne l'entends pas, ce a quoi lui répond sa fille : 'Voyons maman, il faut pas parler la bouche pleine !'",
                                                     "Le sexe c'est comme les équations, à partir de 3 inconnues ça devient intéressant",
                                                     "Un candidat passe l’oral de l’examen de sciences naturelles. L’examinateur plonge la main dans un sac, en sort un petit oiseau dont il montre la queue à l’étudiant:\n– Quel est le nom de cet oiseau ?\n– Heu.. je ne sais pas ! répond l'étudiant.\n– Je vais vous donner une autre chance.\nL’examinateur plonge à nouveau la main dans le sac et en sort un autre oiseau dont à nouveau il monte la queue:\n– Et celui-ci ? Quel est son nom ?\n– Je ne vois vraiment pas, monsieur !\n– Désolé, jeune homme ! Je regret, mais je me vois obliger de vous mettre un zéro ! Au fait, quel est votre nom ?\nLe candidat se lève, ouvre sa braguette et dit:\n– Devinez !",
                                                     "Et que dit-on de deux boules de pétanque qui entrent en collisions ?\nElles partent en couille",
                                                     "peut on appeller une maison vérouillée par son utilisateur lorsqu'il s'en va, une maison close ?",
                                                     "-"]))
    if message.content.startswith(prefix+'yay'):
        f = open("YAY.png","rb")
        yield from client.send_file(message.channel,f,content="YAY !")
        f.close()
    if message.content.startswith(prefix+'setgame') and botowner:
        statut = discord.Game(name=(message.content).replace(prefix+'setgame ',""))
        yield from client.change_presence(game=statut)
    if message.content.startswith(prefix+'choquedecu'):
        f=open("choquedecu.png","rb")
        yield from client.send_file(message.channel,f,content="#choquedecu")
        f.close()
    if message.content.startswith(prefix+'hentai') and nsfw:
        f = open("Hentai/"+choice(os.listdir("Hentai")),"rb")
        yield from client.send_file(message.channel,f)
        f.close()
    if message.content.startswith(prefix+'onichan'):
        f = open("onichan.jpg","rb")
        yield from client.send_file(message.channel,f)
        f.close()
    if message.content.startswith(prefix+'rule34') and nsfw:
        yield from client.send_message(message.channel,"Rule 34 : *If it exists, there is porn on it*\nhttps://rule34.paheal.net/")
    if message.content.startswith(prefix+'suggest'):
        pass
    if message.content.startswith(prefix+'shutdown') and botmanager:
        yield from client.send_message(message.channel,"You are requesting a shutdown, please ensure that you want to perform it by typing `confirm`")
        answer = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content='confirm')
        if answer is None:
            yield from client.send_message(message.channel,"Your request has timeout")
            return
        yield from client.logout()
        sys.exit(0)
    if message.content.startswith(prefix+'blacklist') and botmanager:
        msg = message.content.replace(prefix+'blacklist ',"")
        ls = msg.split(" | ")
        blackid = int(ls[0])
        bl = BDD("userlist")
        bl.load()
        bl["blacklist",str(blackid)] = ls[1]
        bl.save()
        yield from client.send_message(message.channel,"The following id has been blacklisted : `"+str(blackid)+"` for \n```"+ls[1]+"```")
    if message.content.startswith(prefix+'unblacklist') and botmanager:
        blackid = int(message.content.replace(prefix+'unblacklist ',""))
        bl = BDD("userlist")
        bl.load()
        del(bl["blacklist",str(blackid)])
        bl.save()
        yield from client.send_message(message.channel,"The following id has been unblacklisted : `"+str(blackid)+"`")
    if message.content.startswith(prefix+'setbotmanager') and botowner:
        userid = int(message.content.replace(prefix+'setbotmanager ',""))
        user = yield from client.get_user_info(str(userid))
        ul = BDD("userlist")
        ul.load()
        ul["botmanager",str(userid)] = str(user)
        ul.save()
        yield from client.send_message(message.channel,"The ID has been set as botmanager succesful")
    if message.content.startswith(prefix+'setpremium') and botowner:
        userid = int(message.content.replace(prefix+'setpremium ',""))
        user = yield from client.get_user_info(str(userid))
        ul = BDD("userlist")
        ul.load()
        ul["premium",str(userid)] = str(user)
        ul.save()
        yield from client.send_message(message.channel,"The ID has been set as premium succesful")
    if message.content.startswith(prefix+'contentban') and admin:
        content = message.content.replace(prefix+'contentban ',"")
        conf = BDD("config")
        conf.load()
        if str(message.server.id) in conf.file.section["contentban"]:
            ls = convert_str_into_ls_spe(conf["contentban",str(message.server.id)])
        else:
            ls = []
        if len(ls) >= 20:
            yield from client.send_message(message.channel,"Limit of contentban has been reached !\nYou can't add more banned content")
        else:
            ls.append(content)
            temp = str(ls)
            temp = temp.replace("[","{")
            temp = temp.replace("]","}")
            conf["contentban",str(message.server.id)] = temp
            conf.save()
            yield from client.send_message(message.channel,"The following content will now be banned on your server : `"+content+"`")
    if message.content.startswith(prefix+'contentunban') and admin:
        content = message.content.replace(prefix+'contentunban ',"")
        conf = BDD("config")
        conf.load()
        if str(message.server.id) in conf.file.section["contentban"]:
            ls = convert_str_into_ls_spe(conf["contentban",str(message.server.id)])
            while content in ls:
                ls.remove(content)
            yield from client.send_message(message.channel,"The following content has now reauthorized on your server : `"+content+"`")
            temp = str(ls)
            temp = temp.replace("[","{")
            temp = temp.replace("]","}")
            conf["contentban",str(message.server.id)] = temp
            conf.save()
    if message.content.startswith(prefix+'warn') and admin:
        target = []
        for i in message.mentions:
            target.append(str(i))
        targetstr = str(target)
        targetstr = targetstr.replace("[","")
        targetstr = targetstr.replace("]","")
        embd = discord.Embed(title="WARN",description=targetstr,colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(message.timestamp))
        #embd.set_image(url=message.author.avatar_url)
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="https://www.ggte.unicamp.br/ea/img/iconalerta.png")
        embd.add_field(name="Reason :",value=message.content.split("|")[1],inline=True)
        yield from client.send_message(message.channel,embed=embd)
    #Vocal commands
    #Help commands
    if message.content.startswith(prefix+'debug') and botowner:
        msg = (message.content).replace(prefix+'debug ',"")
        print("running debug instruction : "+msg)
        logf.append("/debug","running debug instruction : "+msg)
        exec(msg)
    if message.content.startswith(prefix+'help'):
        f = open("help.txt","r")
        msg = f.read()
        ls = msg.split("\n\n")
        if message.content.startswith(prefix+'help normal'):
            yield from client.send_message(message.author,"Here's the whole list of normal commands :\n"+ls[1])
        elif message.content.startswith(prefix+'help vocal'):
            yield from client.send_message(message.author,"Here's the whole list of vocal commands :\n"+ls[2])
        elif message.content.startswith(prefix+'help JDR'):
            yield from client.send_message(message.author,"Here's the whole list of JDR commands :\n"+ls[3])
        else:
            for i in ls:
                yield from client.send_message(message.author,i)
        f.close()
        yield from client.send_message(message.channel,"I've sent you a private message with the answer")
    if message.content.startswith(prefix+'invite'):
        botaskperm = discord.Permissions().all()
        botaskperm.administrator = botaskperm.ban_members = botaskperm.kick_members = botaskperm.manage_channels = botaskperm.manage_server = botaskperm.manage_roles = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = botaskperm.mute_members = botaskperm.deafen_members = False
        url = discord.utils.oauth_url(str(client.user.id),botaskperm)
        embd = discord.Embed(title="TtgcBot (Alpha)",description="Invite TtgcBot (alpha) to your server !",colour=discord.Color(randint(0,int('ffffff',16))),url=url)
        embd.set_footer(text="TtgcBot version alpha developed by Ttgc",icon_url=client.user.avatar_url)
        embd.set_image(url=client.user.avatar_url)
        embd.set_author(name="Ttgc",icon_url="https://cdn.discordapp.com/avatars/222026592896024576/e1bf51b1158cc87cefcc54afc4849cee.webp?size=1024",url=url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        cfg = BDD("config")
        cfg.load()
        embd.add_field(name="TtgcBot is currently on :",value=str(len(cfg.file.section["prefix"])),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    save_data(message.server.id,charbase,linked)
    logf.stop()
    yield from client.change_presence(game=statut)

@client.event
@asyncio.coroutine
def on_voice_state_update(before,after):
    global vocalco,vocal,anoncer_isready,song
    def reset_anoncer():
        global anoncer_isready
        anoncer_isready = True
    if song == None or song.is_done():
        if before.voice.voice_channel != after.voice.voice_channel and vocal and anoncer_isready:
            if after.voice.voice_channel == vocalco.channel:
                anoncer_isready = False
                anoncer = vocalco.create_ffmpeg_player("Music/reco.mp3",after=reset_anoncer)
                anoncer.start()
                #join
            elif before.voice.voice_channel == vocalco.channel:
                anoncer_isready = False
                anoncer = vocalco.create_ffmpeg_player("Music/deco.mp3",after=reset_anoncer)
                anoncer.start()
                #leave
                
@client.event
@asyncio.coroutine
def on_server_join(server):
    cfg = BDD("config")
    cfg.load()
    cfg["prefix",str(server.id)] = '/'
    cfg.save()
    charbdd = BDD("character")
    charbdd.load()
    charbdd["charbase",str(server.id)] = str({})
    charbdd["charlink",str(server.id)] = str({})
    charbdd.save()

@client.event
@asyncio.coroutine
def on_server_remove(server):
    cfg = BDD("config")
    cfg.load()
    del(cfg["prefix",str(server.id)])
    cfg.save()
    charbdd = BDD("character")
    charbdd.load()
    for i,k in charbdd["charbase",str(server.id)].items():
        del(charbdd["charstat",str(i)])
    del(charbdd["charbase",str(server.id)])
    del(charbdd["charlink",str(server.id)])
    charbdd.save()

@client.event
@asyncio.coroutine
def on_ready():
    global logf
    yield from client.change_presence(game=statut)
    logf.restart()
    conf = BDD("config")
    try: conf.load()
    except:
        conf.create_group("prefix")
        conf.create_group("contentban")
        for i in client.servers:
            conf["prefix",str(i.id)] = '/'
        conf.save()
        logf.append("Initializing","Creating config file")
    charbdd = BDD("character")
    try: charbdd.load()
    except:
        charbdd.create_group("charbase")
        charbdd.create_group("charlink")
        for i in client.servers:
            charbdd["charbase",str(i.id)] = str({})
            charbdd["charlink",str(i.id)] = str({})
        charbdd.create_group("charstat")
        charbdd.save()
        logf.append("Initializing","creating character file")
    if len(client.servers) != len(conf.file.section["prefix"]) or len(client.servers) != len(charbdd.file.section["charbase"]):
        for i in client.servers:
            if not str(i.id) in conf.file.section["prefix"]:
                conf["prefix",str(i.id)] = '/'
            if not str(i.id) in charbdd.file.section["charbase"]:
                charbdd["charbase",str(i.id)] = str({})
                charbdd["charlink",str(i.id)] = str({})
            if len(client.servers) == len(conf.file.section["prefix"]) and len(client.servers) == len(charbdd.file.section["charbase"]): break
        conf.save()
        charbdd.save()
    logf.append("Initializing","Bot is now ready")
    logf.stop()

@asyncio.coroutine
def main_task():
    global TOKEN
    yield from client.login(TOKEN)
    yield from client.connect()

def launch():
    global file,charbase,linked,logf,ideas,events
    logsys = LogSystem()
    logsys.limit = 20
    logsys.directory = "Logs"
    tps = time.localtime()
    logf = Logfile(str(tps.tm_mday)+"_"+str(tps.tm_mon)+"_"+str(tps.tm_year)+"_"+str(tps.tm_hour)+"_"+str(tps.tm_min)+"_"+str(tps.tm_sec),logsys)
    logf.start()
    logf.append("Initializing","Bot initialization...")
    userlist = BDD("userlist")
    try: userlist.load()
    except:
        userlist.create_group("blacklist")
        userlist.create_group("premium")
        userlist.create_group("botmanager")
        userlist.save()
        logf.append("Initializing","creating userlist file")
    logf.append("Initializing","userlist loaded")
    logf.append("Initializing","Bot initialized successful")
    logf.stop()

launch()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main_task())
except:
    loop.run_until_complete(client.logout())
finally:
    loop.close()

