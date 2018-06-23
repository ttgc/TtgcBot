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
from VocalUtilities import *
from Character import *
##from KeepRole import *
from converter import *
import os
import zipfile
import sys
import requests
import subprocess as sub

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

global TOKEN
tokenf = INI()
tokenf.load("token")
TOKEN = tokenf.section["TOKEN"]["Bot"]
del(tokenf)

global logf
global statut
statut = discord.Game(name="Ohayo !")
global vocalcore

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

def get_mjrole(ID):
    ID = str(ID)
    conf = BDD("config")
    conf.load()
    try:
        return conf["MJrole",ID]
    except:
        return None

def command_check(prefix,msg,cmd):
    ctnt = msg.content.split(" ")[0]
    return (ctnt == prefix+cmd)

def save_data(ID,charbase,linked):
    ID = str(ID)
    zp = zipfile.ZipFile("Backup-auto.zip","w")
    for i in os.listdir("Data"):
        zp.write("Data/"+i)
    zp.close()
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
vocalcore = VocalCore()
vocalcore.bot = client

@client.event
@asyncio.coroutine
def on_message(message):
    global TOKEN,vocalcore,logf,statut
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
            yield from client.send_message(message.channel,"I'm sorry but "+message.author.mention+" is currently blacklisted for :\n```"+str(reason)+"\n```")
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
    chanMJ = False
    botmanager = is_botmanager(message.author.id)
    premium = is_premium(message.author.id)
    MJrole = discord.utils.get(message.server.roles,id=get_mjrole(message.server.id))
    MJ = MJrole in message.author.roles
    conf = BDD("config")
    conf.load()
    jdrlist = convert_str_into_dic(conf["JDRchannel",str(message.server.id)])
    if str(message.channel.id) in jdrlist:
        jdrchannel = True
        if MJ: chanMJ = (str(message.author.id) == jdrlist[str(message.channel.id)])
    if botmanager: premium = True
    if str(message.author.id) == "222026592896024576":
        botowner = botmanager = premium = admin = True
    if message.server != None:
        if message.author == message.server.owner: admin = True
    if message.channel.name.startswith("nsfw-"): nsfw = True
    else:
        head = {'Authorization': "Bot "+TOKEN}
        r = requests.get("https://discordapp.com/api/v7/channels/"+str(message.channel.id),headers=head)
        nsfw = r.json()['nsfw']
    if message.channel.id == "237668457963847681": musicchannel = True
    #get charbase
    charbase_exist = True
    try: charbase,linked = get_charbase(message.channel.id)
    except:
        charbase,linked = {},{}
        charbase_exist = False
    char = None
    if str(message.author.id) in linked:
        char = charbase[linked[str(message.author.id)]]
    #get vocal
    vocal = vocalcore.getvocal(str(message.server.id))
    #commands
    #########REWRITTEN##########
    if message.content.startswith(prefix+'setprefix') and admin:
        prefix = (message.content).replace(prefix+'setprefix ',"")
        set_prefix(message.server.id,prefix)
        logf.append("/setprefix","Changing command prefix into : "+prefix)
        yield from client.send_message(message.channel,"Changing command prefix into : "+prefix)
    if message.content.startswith(prefix+'rollindep'):
        expression = message.content.replace(prefix+"rollindep ","")
        expression = expression.replace(" ","")
        expression = expression.replace("-","+-")
        operations = expression.split("+")
        result = []
        for i in operations:
            if "d" in i:
                rdmgen = i.split("d")
                val = int(rdmgen[1])
                repeat_sign = int(rdmgen[0])
                repeat = abs(repeat_sign)
                for k in range(repeat):
                    if repeat_sign < 0:
                        result.append(-randint(1,val))
                    else:
                        result.append(randint(1,val))
            else:
                result.append(int(i))
        final_result = 0
        final_expression = ""
        for i in result:
            final_result += i
            final_expression += str(i)+" + "
        final_expression = final_expression[:-3]
        final_expression = final_expression.replace("+ -","- ")
        yield from client.send_message(message.channel,"You rolled : `"+str(final_result)+"` ("+final_expression+")")
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
        yield from roll(client,message.channel,char,msg,modifier)
    if message.content.startswith(prefix+'charcreate') and chanMJ:
        name = (message.content).replace(prefix+'charcreate ',"")
        if name in charbase:
            yield from client.send_message(message.channel,"This Character already exists use `charselect` to select it and edit it")
            return
        char = Character()
        charbase[name] = char
        yield from client.send_message(message.channel,"Creating new character called : "+name)
    if message.content.startswith(prefix+'chardelete') and chanMJ:
        name = (message.content).replace(prefix+'chardelete ',"")
        yield from client.send_message(message.channel,"Please confirm that you want to delete `"+name+"` by typing `confirm`\nthis cannot be undone !")
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,content="confirm",channel=message.channel)
        if confirm is None:
            yield from client.send_message(message.channel,"Action timeout")
            return
        charbdd = BDD("character")
        charbdd.load()
        del(charbdd["charstat",name])
        charbdd.save()
        del(charbase[name])
        yield from client.send_message(message.channel,"Character deleted")
    if message.content.startswith(prefix+'link') and chanMJ:
        msg = (message.content).replace(prefix+'link ',"")
        name = msg.split(" ")[0]
        if not name in charbase:
            yield from client.send_message(message.channel,"Unexisting character")
            return
        linked[str(message.mentions[0].id)] = name
        yield from client.send_message(message.channel,"Character "+charbase[name].name+" has been succesful linked to "+message.mentions[0].mention)
    if message.content.startswith(prefix+'unlink') and chanMJ:
        if len(message.mentions) == 0:
            del(linked[str(message.author.id)])
            yield from client.send_message(message.channel,"Unlinked "+message.author.mention)
        else:
            del(linked[str(message.mentions[0].id)])
            yield from client.send_message(message.channel,"Unlinked "+message.mentions[0].mention)
    if message.content.startswith(prefix+'charset') and chanMJ:
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
        elif message.content.startswith(prefix+'charset furtivite') or message.content.startswith(prefix+'charset agilite'):
            char.furtivite = int((message.content).split(" ")[3])#replace(prefix+'charset furtivite ',""))
            yield from client.send_message(message.channel,"Changing agilite of character successful")
        elif message.content.startswith(prefix+'charset lp'):
            char.lp += int((message.content).split(" ")[3])#replace(prefix+'charset lp ',""))
            if char.lp < 0: char.lp = 0
            yield from client.send_message(message.channel,"Changing Light Points of character successful")
        elif message.content.startswith(prefix+'charset dp'):
            char.dp += int((message.content).split(" ")[3])#replace(prefix+'charset dp ',""))
            if char.dp < 0: char.dp = 0
            yield from client.send_message(message.channel,"Changing Dark Points of character successful")
        elif message.content.startswith(prefix+'charset defaultmod'):
            ndm = (message.content).split(" ")[3]
            if ndm == "offensiv" or ndm == "defensiv":
                if ndm == "offensiv": ndm = 0
                else: ndm = 1
                char.default_mod = ndm
                yield from client.send_message(message.channel,"Changing default mod of character successful")
        elif message.content.startswith(prefix+'charset defaultkarma'):
            ndk = int((message.content).split(" ")[3])
            if ndk >= -10 and ndk <= 10: char.default_karma = ndk
            yield from client.send_message(message.channel,"Changing default karma of character successful")
        elif message.content.startswith(prefix+'charset intuition'):
            val = int((message.content).split(" ")[3])
            if val >= 1 and val <= 6:
                char.intuition = val
                yield from client.send_message(message.channel,"Changing intuition of character successful")
    if message.content.startswith(prefix+'chardmg') and chanMJ:
        char = charbase[message.content.split(" ")[1]]
        val = abs(int((message.content).split(" ")[2]))#replace(prefix+'chardmg ',""))
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
    if message.content.startswith(prefix+'globaldmg') and chanMJ:
        val = abs(int((message.content).replace(prefix+'globaldmg ',"")))
        embd = discord.Embed(title="Global damage",description="Damage amount : "+str(val),colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        deads = 0
        dead_ls = ""
        playeffect = 0
        for k,i in charbase.items():
            i.PV -= val
            embd.add_field(name=i.name,value=str(i.PV)+" (-"+str(val)+")",inline=True)
            #yield from client.send_message(message.channel,"Character "+i.name+" has lost "+str(val)+" PV")
            #yield from client.send_message(message.channel,"Remaining PV : "+str(i.PV))
            if not i.check_life():
                deads += 1
                dead_ls += (i.name+"\n")
                #yield from client.send_message(message.channel,"Character "+i.name+" is dead !")
                playeffect += 1
                #f = open("you are dead.png","rb")
                #yield from client.send_file(message.channel,f)
                #f.close()
            charbase[k] = i
        if deads > 0:
            embd.add_field(name="Following player(s) is(are) dead :",value=dead_ls,inline=False)
        if deads == len(charbase):
            embd.set_image(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/06/you-are-dead.png")
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'globalheal') and chanMJ:
        val = abs(int((message.content).replace(prefix+'globalheal ',"")))
        embd = discord.Embed(title="Global heal",description="Heal amount : "+str(val),colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        val2 = val
        for k,i in charbase.items():
            i.PV += val2
            val = val2
            if i.PV > i.PVmax:
                val = i.PV - i.PVmax
                i.PV = i.PVmax
            embd.add_field(name=i.name,value=str(i.PV)+" (+"+str(val)+")",inline=True)
            #yield from client.send_message(message.channel,"Character "+i.name+" has been healed from "+str(val)+" PV")
            #yield from client.send_message(message.channel,"Remaining PV : "+str(i.PV))
            charbase[k] = i
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'globalgetPM') and chanMJ:
        val = int((message.content).replace(prefix+'globalgetPM ',""))
        embd = discord.Embed(title="Global getPM",description="PM earned : "+str(val),colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        val2 = val
        for k,i in charbase.items():
            i.PM += val2
            val = val2
            if i.PM > i.PMmax:
                val = i.PM - i.PMmax
                i.PM = i.PMmax
            if i.PM < 0:
                val += i.PM
                i.PM = 0
            sign = "+"
            if val < 0:
                sign = ""
            embd.add_field(name=i.name,value=str(i.PM)+" ("+sign+str(val)+")",inline=True)
            #yield from client.send_message(message.channel,"Character "+i.name+" has got "+str(val)+" PM")
            #yield from client.send_message(message.channel,"Remaining PM : "+str(i.PM))
            charbase[k] = i
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'charheal') and chanMJ:
        char = charbase[message.content.split(" ")[1]]
        val = abs(int((message.content).split(" ")[2]))#replace(prefix+'charheal ',""))
        char.PV += val
        if char.PV > char.PVmax: char.PV = char.PVmax
        yield from client.send_message(message.channel,"Character "+char.name+" has been healed from "+str(val)+" PV")
        yield from client.send_message(message.channel,"Remaining PV : "+str(char.PV))
    if message.content.startswith(prefix+'getPM') and chanMJ:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'getPM ',""))
        if char.PM + val < 0:
            yield from client.send_message(message.channel,"No more PM !")
        else:
            char.PM += val
            if char.PM > char.PMmax: char.PM = char.PMmax
        yield from client.send_message(message.channel,"Remaining PM of character "+char.name+" : "+str(char.PM))
    if message.content.startswith(prefix+'setkarma') and chanMJ:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'setkarma ',""))
        char.karma += val
        if char.karma < -10: char.karma = -10
        if char.karma > 10: char.karma = 10
        yield from client.send_message(message.channel,"Karma of "+char.name+" has currently a value of :"+str(char.karma))
    if message.content.startswith(prefix+'resetchar') and chanMJ:
        char = charbase[message.content.split(" ")[1]]
        char.PV = char.PVmax
        char.PM = char.PMmax
        char.karma = char.default_karma
        char.mod = char.default_mod
        yield from client.send_message(message.channel,"Character has been reset")
    if message.content.startswith(prefix+'pay') and jdrchannel:
        val = int((message.content).replace(prefix+'pay ',""))
        if char.money-val < 0:
            yield from client.send_message(message.channel,"No more money to pay !")
        else:
            if val > 0:
                char.money -= val
        yield from client.send_message(message.channel,"Remaining Money to "+char.name+" : "+str(char.money))
    if message.content.startswith(prefix+'earnmoney') and chanMJ:
        char = charbase[message.content.split(" ")[1]]
        val = int((message.content).split(" ")[2])#replace(prefix+'earnmoney ',""))
        char.money += val
        yield from client.send_message(message.channel,"Remaining Money to "+char.name+" : "+str(char.money))
    if message.content.startswith(prefix+'charinfo') and jdrchannel:
        if char.mod == 0: modd = "Offensiv"
        else: modd = "Defensiv"
        embd = discord.Embed(title=char.name,description=char.lore,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name="PV :",value=str(char.PV)+"/"+str(char.PVmax),inline=True)
        embd.add_field(name="PM :",value=str(char.PM)+"/"+str(char.PMmax),inline=True)
        embd.add_field(name="Mental :",value=str(char.mental),inline=True)
        embd.add_field(name="Intuition :",value=str(char.intuition),inline=True)
        embd.add_field(name="Force :",value=str(char.force),inline=True)
        embd.add_field(name="Esprit :",value=str(char.esprit),inline=True)
        embd.add_field(name="Charisme :",value=str(char.charisme),inline=True)
        embd.add_field(name="Agilite :",value=str(char.furtivite),inline=True)
        embd.add_field(name="Karma :",value=str(char.karma),inline=True)
        embd.add_field(name="Money :",value=str(char.money),inline=True)
        embd.add_field(name="Light Points :",value=str(char.lp),inline=True)
        embd.add_field(name="Dark Points :",value=str(char.dp),inline=True)
        embd.add_field(name="Mod :",value=modd,inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'map') and chanMJ:
        f = open("mapmonde.png","rb")
        yield from client.send_file(message.channel,f)
        f.close()
    if message.content.startswith(prefix+'stat') and jdrchannel:
        embd = discord.Embed(title="Stat of Character",description=char.name,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
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
                elif result == 4: yield from client.send_message(message.channel,"+10%")
                elif result == 5: yield from client.send_message(message.channel,"+20%")
                elif result == 6: yield from client.send_message(message.channel,"No effect")
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
                elif result == 4: yield from client.send_message(message.channel,"-10%")
                elif result == 5: yield from client.send_message(message.channel,"-20%")
                elif result == 6: yield from client.send_message(message.channel,"No effect")
    if message.content.startswith(prefix+'switchmod') and jdrchannel:
        if char.mod == 0:
            char.mod = 1
            yield from client.send_message(message.channel,char.name+" is now on Defensiv mod !")
        else:
            char.mod = 0
            yield from client.send_message(message.channel,char.name+" is now on Offensiv mod !")
    if message.content.startswith(prefix+'setmental') and jdrchannel:
        msg = message.content.replace(prefix+'setmental ',"")
        if "+" in message.content:
            msg = msg.replace("+","")
            char.mental += int(msg)
        elif "-" in message.content:
            msg = msg.replace("-","")
            char.mental -= int(msg)
        else:
            char.mental = int(msg)
        yield from client.send_message(message.channel,"Mental for "+char.name+" is now equal to "+str(char.mental))
    if message.content.startswith(prefix+'mj') and jdrchannel and chanMJ:
        if message.content.startswith(prefix+'mjcharinfo'):
            char = charbase[message.content.split(" ")[1]]
            if char.mod == 0: modd = "Offensiv"
            else: modd = "Defensiv"
            embd = discord.Embed(title=char.name,description=char.lore,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            embd.add_field(name="PV :",value=str(char.PV)+"/"+str(char.PVmax),inline=True)
            embd.add_field(name="PM :",value=str(char.PM)+"/"+str(char.PMmax),inline=True)
            embd.add_field(name="Mental :",value=str(char.mental),inline=True)
            embd.add_field(name="Intuition :",value=str(char.intuition),inline=True)
            embd.add_field(name="Force :",value=str(char.force),inline=True)
            embd.add_field(name="Esprit :",value=str(char.esprit),inline=True)
            embd.add_field(name="Charisme :",value=str(char.charisme),inline=True)
            embd.add_field(name="Agilite :",value=str(char.furtivite),inline=True)
            embd.add_field(name="Karma :",value=str(char.karma),inline=True)
            embd.add_field(name="Money :",value=str(char.money),inline=True)
            embd.add_field(name="Light Points :",value=str(char.lp),inline=True)
            embd.add_field(name="Dark Points :",value=str(char.dp),inline=True)
            embd.add_field(name="Mod :",value=modd,inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if message.content.startswith(prefix+'mjswitchmod'):
            char = charbase[message.content.split(" ")[1]]
            if char.mod == 0:
                char.mod = 1
                yield from client.send_message(message.channel,char.name+" is now on Defensiv mod !")
            else:
                char.mod = 0
                yield from client.send_message(message.channel,char.name+" is now on Offensiv mod !")
        if message.content.startswith(prefix+'mjpay'):
            char = charbase[message.content.split(" ")[1]]
            val = int(message.content.split(" ")[2])
            if char.money-val < 0:
                yield from client.send_message(message.channel,"No more money to pay !")
            else:
                if val > 0:
                    char.money -= val
            yield from client.send_message(message.channel,"Remaining Money to "+char.name+" : "+str(char.money))
        if message.content.startswith(prefix+'mjsetmental'):
            char = charbase[message.content.split(" ")[1]]
            msg = message.content.split(" ")[2]
            if "+" in message.content:
                msg = msg.replace("+","")
                char.mental += int(msg)
            elif "-" in message.content:
                msg = msg.replace("-","")
                char.mental -= int(msg)
            else:
                char.mental = int(msg)
            yield from client.send_message(message.channel,"Mental for "+char.name+" is now equal to "+str(char.mental))
        if message.content.startswith(prefix+'mjroll'):
            char = charbase[message.content.split(" ")[1]]
            msg2 = message.content.split(" ")[2]
            field = (message.content).replace(prefix+'mjroll '+message.content.split(" ")[1]+" "+msg2,"")
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
            yield from roll(client,message.channel,char,msg2,modifier)
    if message.content.startswith(prefix+'setMJrole') and admin:
        conf = BDD("config")
        conf.load()
        conf["MJrole",str(message.server.id)] = str(message.role_mentions[0].id)
        conf.save()
        yield from client.send_message(message.channel,"The role : "+message.role_mentions[0].mention+" has been set as MJ on this server")
    if message.content.startswith(prefix+'JDRstart') and MJ:
        conf = BDD("config")
        conf.load()
        jdrlist = convert_str_into_dic(conf["JDRchannel",str(message.server.id)])
        chan = message.channel_mentions[0]
        if str(chan.id) not in jdrlist:
            jdrlist[str(chan.id)] = str(message.author.id)
            conf["JDRchannel",str(message.server.id)] = str(jdrlist)
            conf.save()
            charbdd = BDD("character")
            charbdd.load()
            charbdd["charbase",str(chan.id)] = str({})
            charbdd["charlink",str(chan.id)] = str({})
            charbdd.save()
            yield from client.send_message(message.channel,"New JDR in "+chan.mention+" (MJ : "+message.author.mention+")")
        else:
            yield from client.send_message(message.channel,"A JDR already exists in "+chan.mention+"\nYou can't create a new one in the same channel")
    if message.content.startswith(prefix+'JDRdelete') and admin:
        conf = BDD("config")
        conf.load()
        jdrlist = convert_str_into_dic(conf["JDRchannel",str(message.server.id)])
        chan = message.channel_mentions[0]
        if str(chan.id) in jdrlist:
            yield from client.send_message(message.channel,"Are you sure you want to delete JDR in "+chan.mention+" ?\nThis cannot be undone !\nType `confirm` to continue")
            confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
            if confirm is None:
                yield from client.send_message(message.channel,"Your action has timeout")
                return
            del(jdrlist[str(chan.id)])
            conf["JDRchannel",str(message.server.id)] = str(jdrlist)
            conf.save()
            charbdd = BDD("character")
            charbdd.load()
            dic = convert_str_into_dic(charbdd["charbase",str(chan.id)])
            for i,k in dic.items():
                del(charbdd["charstat",str(i)])
            del(charbdd["charbase",str(chan.id)])
            del(charbdd["charlink",str(chan.id)])
            charbdd.save()
            charbase_exist = False
            yield from client.send_message(message.channel,"JDR in "+chan.mention+" has been deleted succesful")
    if message.content.startswith(prefix+'MJtransfer') and chanMJ:
        if not MJrole in message.mentions[0].roles:
            yield from client.send_message(message.channel,"I'm sorry but you can transfer ownership only to an other MJ")
            return
        yield from client.send_message(message.channel,"Would you transfer ownership of JDR in "+message.channel.mention+" to "+message.mentions[0].mention+" ?\ntype `confirm` to continue")
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,"This action has timeout")
            return
        yield from client.send_message(message.channel,message.mentions[0].mention+"\n"+message.author.mention+" Want to give you the ownership of JDR in : "+message.channel.mention+"\nType `accept` to accept this")
        confirm = yield from client.wait_for_message(timeout=60,author=message.mentions[0],channel=message.channel,content="accept")
        if confirm is None:
            yield from client.send_message(message.channel,message.mentions[0].mention+" doesn't accept or answer in time your proposition")
            return
        conf = BDD("config")
        conf.load()
        jdrlist = convert_str_into_dic(conf["JDRchannel",str(message.server.id)])
        jdrlist[str(message.channel.id)] = str(message.mentions[0].id)
        conf["JDRchannel",str(message.server.id)] = str(jdrlist)
        conf.save()
        yield from client.send_message(message.channel,"Ownership belong now to : "+message.mentions[0].mention)
    if message.content.startswith(prefix+'JDRcopy') and admin:
        if message.channel_mentions[0].server.id != message.server.id or message.channel_mentions[0].server.id != message.channel_mentions[1].server.id:
            yield from client.send_message(message.channel,"channels are not located on the same server")
            return
        yield from client.send_message(message.channel,"Would you copy data from "+message.channel_mentions[0].mention+" to "+message.channel_mentions[1].mention+" ?\nAll data in the destination channel will be replaced by the new one, are you sure ?\ntype `confirm` to continue")
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,"This action has timeout")
            return
        src = message.channel_mentions[0]
        dest = message.channel_mentions[1]
        conf = BDD("config")
        conf.load()
        jdrlist = convert_str_into_dic(conf["JDRchannel",str(message.server.id)])
        jdrlist[str(dest.id)] = jdrlist[str(src.id)]
        conf["JDRchannel",str(message.server.id)] = str(jdrlist)
        conf.save()
        charbdd = BDD("character")
        charbdd.load()
        charbdd["charbase",str(dest.id)] = charbdd["charbase",str(src.id)]
        charbdd["charlink",str(dest.id)] = charbdd["charlink",str(src.id)]
        charbdd.save()
        yield from client.send_message(message.channel,"JDR copied successfull")
    if message.content.startswith(prefix+'wiki'):
        query = message.content.replace(prefix+'wiki ',"")
        query = query.replace(" ","_")
        info = requests.get("http://thetaleofgreatcosmos.fr/wiki/api.php?action=parse&page="+query+"&format=json&redirects=true")
        exist_test = requests.get("http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query)
        if exist_test.status_code != 200:
            yield from client.send_message(message.channel,"Unexisting page. Statuts code : `"+str(exist_test.status_code)+"`")
            return
        descrip = info.json()["parse"]["text"]["*"]
        descrip = descrip.split("</p>")[0]
        while descrip.find("<") != -1:
            descrip = descrip[:descrip.find("<")]+descrip[descrip.find(">")+1:]
        if info.json()["parse"]["text"]["*"].find("<img") == -1:
            img = None
        else:
            pos = info.json()["parse"]["text"]["*"].find("<img")
            temp = info.json()["parse"]["text"]["*"]
            temp = temp[pos+1:]
            temp = temp[:temp.find("/>")]
            temp = temp[temp.find("src=")+5:]
            img = "http://thetaleofgreatcosmos.fr"+temp.split('"')[0]        
        embd = discord.Embed(title=info.json()["parse"]["title"],description=descrip,url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query,colour=discord.Color(randint(0,int('ffffff',16))))
        embd.set_footer(text="The Tale of Great Cosmos - Wiki")
        if img is not None:
            embd.set_image(url=img)
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url,url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        if len(info.json()["parse"]["redirects"]) != 0:
            embd.add_field(name="Redirected from :",value=info.json()["parse"]["redirects"][0]["from"],inline=True)
        yield from client.send_message(message.channel,embed=embd)
    #####NOT YET REWRITTEN######
    if message.content.startswith(prefix+'finalize') and chanMJ and botowner:
        yield from client.send_message(message.channel,"Finalize command has been called !\nPlease be sure of what you are doing, there is no come back !\nEnter `confirm finalize` to start finalize operation (this will timeout in 60s without answer)")
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm finalize")
        if confirm is None:
            yield from client.send_message(message.channel,"Finalize has timeout ! It won't be performed")
            return
        yield from client.send_message(message.channel,"Starting finalize operation")
        anoncer_isready = False
        f = open("finalizer.txt","r")
        ftxt = f.read()
        f.close()
        msg = ftxt.split("\n\n")
        if vocal:
            yield from vocal.append("Music/never_give_up_tsfh.mp3",False)#above_and_beyond_audiomachine.mp3",False)
            vocal.play()
        time.sleep(2)
        embd = discord.Embed(title="The Tale of Great Cosmos",colour=discord.Color(int("5B005B",16)))
        embd.set_image(url="https://cdn.discordapp.com/attachments/254997041858478080/317324181542928395/The_Tale_of_Great_Cosmos.png")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_footer(text=time.asctime())
        yield from client.send_message(message.channel,embed=embd)
        time.sleep(5)
        for i in msg:
            titl,cont = i[:i.find("\n")],i[i.find("\n")+1:]
            if titl.find(":") == -1:
                titl = "The Tale of Great Cosmos"
                cont = i
            embd = discord.Embed(title=titl,description=cont,colour=discord.Color(int("5B005B",16)))
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_footer(text=time.asctime())
            yield from client.send_message(message.channel,embed=embd)
            time.sleep(10)
        thanksmsg = yield from client.send_message(message.channel,"Thanks for playing **The Tale of Great Cosmos** !")
        yield from client.add_reaction(thanksmsg,"\U0001F4AF")
        yield from client.add_reaction(thanksmsg,"\U0001F51A")
        yield from client.add_reaction(thanksmsg,"\U0001F1EA")
        yield from client.add_reaction(thanksmsg,"\U0001F1F3")
        yield from client.add_reaction(thanksmsg,"\U0001F1E9")
        pined = yield from client.pins_from(message.channel)
        os.mkdir("Finalize")
        for i in pined:
            f = open("Finalize/"+i.id+".txt","w+")
            f.write(i.content)
            if len(i.attachments) != 0:
                f.write("\n\n--Atachments--\n")
                for k in i.attachments:
                    f.write(k["filename"]+" - "+k["url"]+"\n")
            f.close()
            #yield from client.unpin_message(i)
        zp = zipfile.ZipFile("The Tale of Great Cosmos - Pined Archive.zip","w")
        for i in os.listdir("Finalize"):
            zp.write("Finalize/"+i)
        zp.close()
        for i in os.listdir("Finalize"):
            os.remove("Finalize/"+i)
        os.rmdir("Finalize")
        yield from client.send_file(message.channel,"The Tale of Great Cosmos - Pined Archive.zip")
        yield from client.send_message(message.channel,"Finalize is now over, see you soon for a next Party !")
        anoncer_isready = True
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
    if command_check(prefix,message,'pi'):
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
        yield from vocalcore.interupt()
        yield from client.logout()
        sys.exit(0)
    if message.content.startswith(prefix+'reboot') and botmanager:
        yield from client.send_message(message.channel,"You are requesting a reboot, please ensure that you want to perform it by typing `confirm`")
        answer = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content='confirm')
        if answer is None:
            yield from client.send_message(message.channel,"Your request has timeout")
            return
        yield from vocalcore.interupt()
        yield from client.logout()
        sub.call(['./bootbot.sh'])
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
        conf = BDD("config")
        conf.load()
        try: warnls = conf["warnuser",str(message.server.id)]
        except: warnls = "{}"
        warnls = convert_str_into_dic(warnls)
        target = []
        warncount = []
        for i in message.mentions:
            target.append(str(i))
            try: warnls[str(i.id)] = str(int(warnls[str(i.id)])+1)
            except: warnls[str(i.id)] = "1"
            warncount.append(warnls[str(i.id)])
        conf["warnuser",str(message.server.id)] = str(warnls)
        conf.save()
        targetstr = str(target)
        targetstr = targetstr.replace("[","")
        targetstr = targetstr.replace("]","")
        targetstr = targetstr.replace("'","")
        countstr = ""
        for i in range(len(target)):
            countstr += (target[i]+" : "+warncount[i]+"\n")
        embd = discord.Embed(title="WARN",description=targetstr,colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(message.timestamp))
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="https://www.ggte.unicamp.br/ea/img/iconalerta.png")
        embd.add_field(name="Reason :",value=message.content.split("|")[1],inline=True)
        embd.add_field(name="Total warnings :",value=countstr,inline=True)
        yield from client.send_message(message.channel,embed=embd)
        try: warnval = conf["warn",str(message.server.id)]
        except: warnval = "{}"
        warnval = convert_str_into_dic(warnval)
        for i in range(len(warncount)):
            if warncount[i] in warnval:
                try:
                    if warnval[warncount[i]] == "kick":
                        yield from client.kick(message.mentions[i])
                        yield from client.send_message(message.channel,target[i]+" has been kicked due to a high number of warnings")
                        yield from client.send_message(message.mentions[i],"You have been **kicked** from : "+message.server.name+" due to a high number of warnings")
                    elif warnval[warncount[i]] == "ban":
                        yield from client.ban(message.mentions[i],0)
                        yield from client.send_message(message.channel,target[i]+" has been banned due to a high number of warnings")
                        yield from client.send_message(message.mentions[i],"You have been **banned** from : "+message.server.name+" due to a high number of warnings")
                    else:
                        rl = None
                        for k in message.server.roles:
                            if str(k.id) == warnval[warncount[i]]: 
                                rl = k
                                break;
                        if rl is not None:
                            yield from client.add_roles(message.mentions[i],rl)
                            yield from client.send_message(message.channel,message.mentions[i].mention+" has got role "+rl.mention+" due to a high number of warnings")
                except discord.Forbidden: pass
    if message.content.startswith(prefix+'configwarn') and admin:
        msg = message.content.replace(prefix+'configwarn ',"")
        value = int(msg.split(" ")[0])
        sanction = msg.split(" ")[1].lower()
        conf = BDD("config")
        conf.load()
        try: warnls = conf["warn",str(message.server.id)]
        except: warnls = "{}"
        warnls = convert_str_into_dic(warnls)
        if sanction == "assign":
            rl = message.role_mentions[0]
            warnls[str(value)] = str(rl.id)
            yield from client.send_message(message.channel,"Assigned role assignement ("+rl.mention+") punishment for people with "+str(value)+" warnings")
            conf["warn",str(message.server.id)] = str(warnls)
            conf.save()
            pass
        elif sanction == "kick":
            warnls[str(value)] = "kick"
            yield from client.send_message(message.channel,"Assigned kick punishment for people with "+str(value)+" warnings")
            conf["warn",str(message.server.id)] = str(warnls)
            conf.save()
            pass
        elif sanction == "ban":
            warnls[str(value)] = "ban"
            yield from client.send_message(message.channel,"Assigned ban punishment for people with "+str(value)+" warnings")
            conf["warn",str(message.server.id)] = str(warnls)
            conf.save()
            pass
        elif sanction == "remove":
            try: del(warnls[str(value)])
            except: pass
            conf["warn",str(message.server.id)] = str(warnls)
            conf.save()
            yield from client.send_message(message.channel,"Removing punishment for people with "+str(value)+" warnings")
        else:
            yield from client.send_message(message.channel,"Unknown punishment type for warn command")
##BLOCKED UNTIL RESOLUTION OF ISSUES
##
##    #KeepRole commands
##    if message.content.startswith(prefix+'keeprole') and admin:
##        kr = KeepRoleServer(str(message.server.id))
##        info = yield from client.application_info()
##        if not message.server.get_member(info.id).server_permissions.manage_roles:
##            yield from client.send_message(message.channel,"I'm not allowed to manage roles")
##            return
##        if message.content.startswith(prefix+'keeprole enabled'):
##            msg = message.content.replace(prefix+'keeprole enabled ',"")
##            msg = msg.lower()
##            if (msg == "true" or msg == "1") and (not kr.enabled):
##                kr.switch()
##                yield from client.send_message(message.channel,"KeepRole enabled on this server")
##            elif (msg == "false" or msg == "0") and kr.enabled:
##                kr.switch()
##                kr.setmembers({})
##                yield from client.send_message(message.channel,"KeepRole disabled on this server")
##        if message.content.startswith(prefix+'keeprole roles add'):
##            ls = []
##            strls = ""
##            for i in message.role_mentions:
##                if i.position < message.server.get_member(info.id).top_role.position:
##                    ls.append(str(i.id))
##                    strls += ("\n"+i.mention)
##            kr.addroles(ls)
##            yield from client.send_message(message.channel,"Adding following roles to KeepRole system : "+strls)
##        if message.content.startswith(prefix+'keeprole roles delete'):
##            ls = []
##            strls = ""
##            for i in message.role_mentions:
##                if str(i.id) in kr.roles and i.position < message.server.get_member(info.id).top_role.position:
##                    ls.append(str(i.id))
##                    strls += ("\n"+i.mention)
##            kr.removeroles(ls)
##            yield from client.send_message(message.channel,"Deleting following roles from KeepRole system : "+strls)
##        if message.content.startswith(prefix+'keeprole clear'):
##            kr.setmembers({})
##            yield from client.send_message(message.channel,"KeepRole members list purged successful")
##
##END OF BLOCUS
    #Vocal commands
    if message.content.startswith(prefix+'vocal') and premium:
        msg = (message.content).replace(prefix+'vocal ',"")
        msg = msg.lower()
        if msg == "on" and not client.is_voice_connected(message.server):
            vocal = VocalSystem(str(message.server.id),vocalcore)
            yield from vocal.join(message.author.voice.voice_channel,message.channel)
            yield from client.send_message(vocal.textchan,":white_check_mark: Connecting to vocal `"+str(message.author.voice.voice_channel)+"` and binding to `"+str(vocal.textchan)+"`")
        elif msg == "off" and client.is_voice_connected(message.server) and (vocal is not None) and ((vocal.textchan == message.channel) or admin):
            chan = vocal.textchan
            yield from vocal.leave()
            vocalcore.removefromlist(str(message.server.id))
            yield from client.send_message(chan,"Disconnected from vocal")
    if message.content.startswith(prefix+'ytplay') and (vocal is not None) and vocal.vocal and (vocal.textchan == message.channel) and premium:
        msg = (message.content).replace(prefix+'ytplay ',"")
        yield from vocal.append(msg)
        vocal.play()
        yield from client.send_message(vocal.textchan,":arrow_forward: Adding song to queue")
    if message.content.startswith(prefix+'musicskip') and (vocal is not None) and vocal.vocal and (vocal.textchan == message.channel) and premium:
        vocal.skip()
        yield from client.send_message(vocal.textchan,":fast_forward: Skiping song")
    if message.content.startswith(prefix+'playlocal') and premium and (vocal is not None) and vocal.vocal and (vocal.textchan == message.channel):
        msg = (message.content).replace(prefix+'playlocal ',"")
        if not msg in os.listdir("Music/"):
            if msg+".mp3" in os.listdir("Music/"): msg += ".mp3"
            elif msg+".wav" in os.listdir("Music/"): msg += ".wav"
            else:
                yield from client.send_message(message.channel,"file not found")
                return
        yield from vocal.append("Music/"+msg,False)
        vocal.play()
        yield from client.send_message(vocal.textchan,":arrow_forward: Adding local song to queue")
    if message.content.startswith(prefix+'disconnectvocal') and botmanager:
        yield from client.send_message(message.channel,"This will disconnect the bot from all vocal connections, are you sure ?\nType `confirm` to do it")
        answer = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content='confirm')
        if answer is None:
            yield from client.send_message(message.channel,"Your request has timeout")
            return
        yield from vocalcore.interupt()
    if message.content.startswith(prefix+'apart') and chanMJ and message.author.voice.voice_channel is not None:
        if len(message.mentions) == 0:
            ls = list(message.author.voice.voice_channel.voice_members)
            for i in ls:
                if i.id in linked or i == message.author:
                    yield from client.server_voice_state(i,mute=False,deafen=False)
        else:
            ls = list(message.author.voice.voice_channel.voice_members)
            for i in ls:
                if i.id in linked or i == message.author:
                    if i in message.mentions or i == message.author:
                        yield from client.server_voice_state(i,mute=False,deafen=False)
                    else:
                        yield from client.server_voice_state(i,mute=True,deafen=True)
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
            yield from client.send_message(message.author,"Here's the whole list of normal commands :\n"+ls[0])
        elif message.content.startswith(prefix+'help vocal'):
            yield from client.send_message(message.author,"Here's the whole list of vocal commands :\n"+ls[1])
        elif message.content.startswith(prefix+'help JDR'):
            yield from client.send_message(message.author,"Here's the whole list of JDR commands :\n"+ls[2])
            yield from client.send_message(message.author,ls[3])
        else:
            yield from client.send_message(message.author,"Here's the whole list of my commands (somes will need some rights) :\n")
            for i in ls:
                yield from client.send_message(message.author,i)
        f.close()
        yield from client.send_message(message.channel,"I've sent you a private message with the answer")
    if message.content.startswith(prefix+'invite'):
        botaskperm = discord.Permissions().all()
        botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_server = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
        url = discord.utils.oauth_url(str(client.user.id),botaskperm)
        embd = discord.Embed(title="TtgcBot (Beta)",description="Invite TtgcBot (beta) to your server !",colour=discord.Color(randint(0,int('ffffff',16))),url=url)
        embd.set_footer(text="TtgcBot version beta developed by Ttgc",icon_url=client.user.avatar_url)
        embd.set_image(url=client.user.avatar_url)
        embd.set_author(name="Ttgc",icon_url="https://cdn.discordapp.com/avatars/222026592896024576/e1bf51b1158cc87cefcc54afc4849cee.webp?size=1024",url=url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        cfg = BDD("config")
        cfg.load()
        embd.add_field(name="TtgcBot is currently on :",value=str(len(cfg.file.section["prefix"])),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'jointhegame'):
        inv = yield from client.create_invite(client.get_server("326648561976737792"),max_age=3600)
        yield from client.send_message(message.channel,"Rejoignez le serveur officiel The Tale of Great Cosmos (serveur FR) : \n"+str(inv.url))
    if message.content.startswith(prefix+'ping'):
        tps_start = time.clock()
        yield from client.send_message(message.channel,":ping_pong: pong ! :ping_pong:")
        tps_end = time.clock()
        ping = round((tps_end-tps_start)*1000)
        yield from client.send_message(message.channel,"ping value is currently : `"+str(ping)+" ms`")
    if message.content.startswith(prefix+'backup') and botowner:
        zp = zipfile.ZipFile("Backup.zip","w")
        for i in os.listdir("Data"):
            zp.write("Data/"+i)
        zp.close()
        yield from client.send_file(message.author,"Backup.zip")
    if charbase_exist:
        try: save_data(message.channel.id,charbase,linked)
        except:
            me = yield from client.get_user_info("222026592896024576")
            yield from client.send_file(me,"Backup-auto.zip",content="An error has occured when saving database, maybe some file has been corrupted, here is the autogenerated backup")
            yield from client.send_message(me,"The following user has made this shit : "+str(message.author)+" (ID="+str(message.author.id)+")")
            yield from client.send_message(message.author,"Your command has failed ! It has created a black hole in my system. If new commands following this doesn't work, please wait until a god close this black hole")
            yield from client.send_message(me,"Here is the list of things that I can do for trying to fix the problem :\n```\nrestore - Restore the database from auto-backup\nblacklist - Blacklist the user who cause crash\nshutdown - Shutdown me\neval - evaluate damage by checking size of files (allow to use another command after)\n```Answer to this with option selected, separate them with `|` to use many options")
            os.rename("Backup-auto.zip","Backup-auto-save.zip")
            cmd = yield from client.wait_until_message(author=me,channel=me)
            while " " in cmd: cmd.replace(" ","")
            cmd_list = cmd.lower().split("|")
            for i in cmd_list:
                if i == "restore":
                    zpcor = zipfile.ZipFile("Backup-corrupted.zip","w")
                    for k in os.listdir("Data"):
                        zp.write("Data/"+k)
                    zp.close()
                    zp = zipfile.ZipFile("Backup-auto-save.zip","r")
                    zp.exctractall()
                    zp.close()
                    yield from client.send_file(me,"Backup-corrupted.zip",content="Restored database, here is old database :")
                    os.remove("Backup-corrupted.zip")
                elif i == "blacklist":
                    blackid = int(message.author.id)
                    bl = BDD("userlist")
                    bl.load()
                    bl["blacklist",str(blackid)] = "Making crash the bot"
                    bl.save()
                    yield from client.send_message(me,"The following id has been blacklisted : `"+str(blackid)+"` for \n```Making crash the bot```")
                elif i == "eval":
                    string = "Eval result :\n```\n"
                    for k in os.listdir("Data"):
                        string += k+" - "
                        string += str(os.stat("Data/"+k).st_size)+"Bytes\n"
                    string += "```"
                    yield from client.send_message(me,string)
                    yield from client.send_message(me,"Here is the list of things that I can do for trying to fix the problem :\n```\nrestore - Restore the database from auto-backup\nblacklist - Blacklist the user who cause crash\nshutdown - Shutdown me\n```Answer to this with option selected, separate them with `|` to use many options")
                    cmd = yield from client.wait_until_message(author=me,channel=me)
                    while " " in cmd: cmd.replace(" ","")
                    cmd_list += cmd.lower().split("|")
                elif i == "shutdown":
                    yield from client.logout()
                    sys.exit(0)
    logf.stop()
    yield from client.change_presence(game=statut)

@client.event
@asyncio.coroutine
def on_voice_state_update(before,after):
    global vocalcore
    vocal = vocalcore.getvocal(str(after.server.id))
    if (vocal is not None) and vocal.vocal and (not vocal.is_playing) and before.voice.voice_channel != after.voice.voice_channel:
        if after.voice.voice_channel == vocal.co.channel:
            yield from vocal.append("Music/reco.mp3",False)
            vocal.play()
            #join
        elif before.voice.voice_channel == vocal.co.channel:
            yield from vocal.append("Music/deco.mp3",False)
            vocal.play()
            #leave

##BLOCKED UNTIL RESOLUTION OF ISSUES
##
##@client.event
##@asyncio.coroutine
##def on_member_join(member):
##    kr = KeepRoleServer(str(member.server.id))
##    if kr.enabled:
##        yield from kr.apply(client)
##
##@client.event
##@asyncio.coroutine
##def on_member_remove(member):
##    kr = KeepRoleServer(str(member.server.id))
##    if kr.enabled:
##        rolels = []
##        for i in member.roles:
##            if str(i.id) in kr.roles:
##                rolels.append(str(i.id))
##        kr.addmembers({str(member.id):rolels})
##
##END OF BLOCUS
                
@client.event
@asyncio.coroutine
def on_server_join(server):
    cfg = BDD("config")
    cfg.load()
    cfg["prefix",str(server.id)] = '/'
    cfg["JDRchannel",str(server.id)] = str({})
    cfg.save()

@client.event
@asyncio.coroutine
def on_server_remove(server):
    cfg = BDD("config")
    cfg.load()
    del(cfg["prefix",str(server.id)])
    try: del(cfg["contentban",str(server.id)])
    except: pass
    try: del(cfg["MJrole",str(server.id)])
    except: pass
    del(cfg["JDRchannel",str(server.id)])
    cfg.save()
    charbdd = BDD("character")
    charbdd.load()
    for j in server.channels:
        try:
            for i,k in charbdd["charbase",str(j.id)].items():
                del(charbdd["charstat",str(i)])
            del(charbdd["charbase",str(j.id)])
            del(charbdd["charlink",str(j.id)])
        except: pass
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
        conf.create_group("MJrole")
        conf.create_group("JDRchannel")########
        for i in client.servers:
            conf["prefix",str(i.id)] = '/'
            conf["JDRchannel",str(i.id)] = str({})
        conf.save()
        logf.append("Initializing","Creating config file")
    charbdd = BDD("character")
    try: charbdd.load()
    except:
        charbdd.create_group("charbase")
        charbdd.create_group("charlink")
        charbdd.create_group("charstat")
        charbdd.create_group("warn")
        charbdd.create_group("warnuser")
        charbdd.save()
        logf.append("Initializing","creating character file")
    krsys = BDD("keeprole")
    try: krsys.load()
    except:
        krsys.create_group("servers")
        krsys.create_group("members")
        krsys.create_group("roles")
        krsys["servers","list"] = "{}"
        krsys["servers","enabled"] = "{}"
        krsys.save()
        logf.append("Initializing","creating keeprole file")
    
    if len(client.servers) != len(conf.file.section["prefix"]): #or len(client.servers) != len(charbdd.file.section["charbase"]):
        for i in client.servers:
            if not str(i.id) in conf.file.section["prefix"]:
                conf["prefix",str(i.id)] = '/'
                conf["JDRchannel",str(i.id)] = str({})
            if len(client.servers) == len(conf.file.section["prefix"]): break #and len(client.servers) == len(charbdd.file.section["charbase"]): break
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
    global logf
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

