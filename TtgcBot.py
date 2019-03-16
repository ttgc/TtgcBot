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
from parsingdice import *
import logging
import time
#from EventManager import *
from VocalUtilities import *
from Character import *
from CharacterUtils import *
from converter import *
from BotTools import *
from Translator import *
from mapmanager import *
import os
import zipfile
import sys
import requests
import subprocess as sub
import traceback

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

def deprecated(func):
    """Deprecated decorator"""
    def func_deprecated():
        raise RuntimeError("function {0} is deprecated !".format(func))
    return func_deprecated

def sum_ls(ls1,ls2):
    lsf = ls1[:]
    for i in range(len(lsf)):
        lsf[i] += ls2[i]
    return lsf

@deprecated
def get_prefix(ID):
    srv = DBServer(ID)
    return srv.prefix

@deprecated
def set_prefix(ID,new):
    srv = DBServer(ID)
    srv.setprefix(new)

def is_blacklisted(ID):
    try: member = DBMember(ID)
    except: return False,""
    bl,rs = member.is_blacklisted()
    return bl,rs

def is_botmanager(ID):
    try: member = DBMember(ID)
    except: return False
    return member.is_manager()

def is_premium(ID):
    try: member = DBMember(ID)
    except: return False
    return member.is_premium()

def is_owner(ID):
    try: member = DBMember(ID)
    except: return False
    return member.is_owner()

@deprecated
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

@deprecated
def get_mjrole(ID):
    srv = DBServer(ID)
    return srv.mjrole

def command_check(prefix,msg,cmd,aliases=[]):
    check = (msg.content.startswith(prefix+cmd+" ") or msg.content == prefix+cmd)#(ctnt == prefix+cmd)
    for i in aliases:
        check = (check or (msg.content.startswith(prefix+i+" ") or msg.content == prefix+i))
    return check

def get_args(prefix,msg,cmd,aliases=[]):
    if not command_check(prefix,msg,cmd,aliases):
        return ""
    work = [cmd]+list(aliases)
    for i in work:
        if command_check(prefix,msg,i):
            return msg.content.replace(prefix+i+" ","")
    return ""

@deprecated
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
    #get server information
    srv = DBServer(message.server.id)
    #get prefix
    prefix = srv.prefix
    #get language
    lgcode = getuserlang(message.author.id)
    if not lang_exist(lgcode): lgcode = "EN"
    lang = get_lang(lgcode)
    #blacklisting
    blacklisted, reason = is_blacklisted(message.author.id)
    if blacklisted:
        if message.content.startswith(prefix):
            yield from client.send_message(message.channel,lang["blacklisted"].format(message.author.mention,str(reason)))
        return
    #message check
    if not message.content.startswith(prefix):
        filtre = srv.wordblocklist()
        for i in filtre:
            if i in message.content:
                yield from client.delete_message(message)
                yield from client.send_message(message.author,lang["contentbanned"])
                return
    #special values
    jdrchannel = False
    admin = discord.utils.get(message.server.roles,id=srv.adminrole) in message.author.roles
    if message.author == message.server.owner: admin = True
    nsfw = False
    musicchannel = False
    chanMJ = False
    botmanager = is_botmanager(message.author.id)
    premium = is_premium(message.author.id)
    botowner = is_owner(message.author.id)
    MJrole = discord.utils.get(message.server.roles,id=srv.mjrole)
    MJ = MJrole in message.author.roles
    jdrlist = srv.jdrlist()
    for i in jdrlist:
        if str(message.channel.id) == i[0]:
            jdrchannel = True
            if MJ: chanMJ = (str(message.author.id) == i[3])
            break
    if not jdrchannel:
        ext = srv.jdrextension()
        if str(message.channel.id) in ext:
            jdrchannel = True
            if MJ: chanMJ = (str(message.author.id) == srv.getJDR(str(message.channel.id)).mj)
    if message.channel.name.startswith("nsfw-"): nsfw = True
    else:
        head = {'Authorization': "Bot "+TOKEN}
        r = requests.get("https://discordapp.com/api/v7/channels/"+str(message.channel.id),headers=head)
        try: nsfw = r.json()['nsfw']
        except: nsfw = False
    if message.channel.id == "237668457963847681": musicchannel = True
    #get charbase
    jdr = None
    charbase_exist = False
    if jdrchannel:
        jdr = srv.getJDR(message.channel.id)
        charbase_exist = True
        charbase = jdr.get_charbase()
        member_charbase = []
        for i in charbase:
            if i.linked == str(message.author.id):
                member_charbase.append(i)
                if i.selected: char = i
    #get vocal
    vocal = vocalcore.getvocal(str(message.server.id))

    #commands
    if command_check(prefix,message,'setprefix',['prefix']) and admin:#message.content.startswith(prefix+'setprefix') and admin:
        prefix = get_args(prefix,message,'setprefix',['prefix'])#(message.content).replace(prefix+'setprefix ',"")
        srv.setprefix(prefix)
        logf.append("/setprefix","Changing command prefix into : "+prefix)
        yield from client.send_message(message.channel,lang["setprefix"].format(prefix))
    if command_check(prefix,message,'rollindep',['rolldice','r']):#message.content.startswith(prefix+'rollindep'):
        expression = get_args(prefix,message,'rollindep',['rolldice','r'])#message.content.replace(prefix+"rollindep ","")
        parser = ParseRoll(expression)
        final_result,final_expression = parser.resolv()
        # expression = expression.replace(" ","")
        # expression = expression.replace("-","+-")
        # operations = expression.split("+")
        # result = []
        # for i in operations:
        #     if "d" in i:
        #         rdmgen = i.split("d")
        #         val = int(rdmgen[1])
        #         repeat_sign = int(rdmgen[0])
        #         repeat = abs(repeat_sign)
        #         for k in range(repeat):
        #             if repeat_sign < 0:
        #                 result.append(-randint(1,val))
        #             else:
        #                 result.append(randint(1,val))
        #     else:
        #         result.append(int(i))
        # final_result = 0
        # final_expression = ""
        # for i in result:
        #     final_result += i
        #     final_expression += str(i)+" + "
        # final_expression = final_expression[:-3]
        # final_expression = final_expression.replace("+ -","- ")
        yield from client.send_message(message.channel,lang["rollindep"].format(final_result,final_expression))

    #jdr commands
    if command_check(prefix,message,'roll') and jdrchannel:#message.content.startswith(prefix+'roll') and jdrchannel:
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
        if not char.dead:
            yield from char.roll(client,message.channel,lang,msg,modifier)
        else:
            yield from client.send_message(message.channel,lang["is_dead"].format(char.name))
    if command_check(prefix,message,'charcreate',['createchar']) and chanMJ:#message.content.startswith(prefix+'charcreate') and chanMJ:
        args = get_args(prefix,message,'charcreate',['createchar']).split(" ")#(message.content).replace(prefix+'charcreate ',"")
        name = args[2]
        race = retrieveRaceID(args[0].replace("_"," "))
        classe = retrieveClassID(race,args[1].replace("_"," "))
        if (race is None or classe is None):
            yield from client.send_message(message.channel,lang["unknown_class"])
            return
        if name in charbase:
            yield from client.send_message(message.channel,lang["charcreate_existing"])
            return
        jdr.charcreate(name,classe)
        yield from client.send_message(message.channel,lang["charcreate"].format(name))
    if command_check(prefix,message,'chardelete',['deletechar','delchar','chardel']) and chanMJ:#message.content.startswith(prefix+'chardelete') and chanMJ:
        name = get_args(prefix,message,'chardelete',['deletechar','delchar','chardel'])#(message.content).replace(prefix+'chardelete ',"")
        yield from client.send_message(message.channel,lang["chardelete_confirm"].format(name))
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,content="confirm",channel=message.channel)
        if confirm is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        jdr.chardelete(name)
        yield from client.send_message(message.channel,lang["chardelete"])
    if command_check(prefix,message,'link',['charlink']) and chanMJ:#message.content.startswith(prefix+'link') and chanMJ:
        msg = get_args(prefix,message,'link',['charlink'])#(message.content).replace(prefix+'link ',"")
        name = msg.split(" ")[0]
        character = jdr.get_character(name)
        character.link(message.mentions[0].id)
        yield from client.send_message(message.channel,lang["charlink"].format(character.name,message.mentions[0].mention))
    if command_check(prefix,message,'unlink',['charunlink']) and chanMJ:#message.content.startswith(prefix+'unlink') and chanMJ:
        if get_args(prefix,message,'unlink',['charunlink']) == "":
            char.unlink()
            yield from client.send_message(message.channel,lang["charunlink"].format(char.name))
        else:
            character = jdr.get_character(get_args(prefix,message,'unlink',['charunlink']))
            character.unlink()
            yield from client.send_message(message.channel,lang["charunlink"].format(character.name))
    if command_check(prefix,message,'charselect') and jdrchannel:
        key = get_args(prefix,message,'charselect')
        for i in member_charbase:
            if i.key == key and i.link == str(message.author.id):
                i.select()
                yield from client.send_message(message.channel,lang["charselect"].format(char.key,i.key))
            else:
                yield from client.send_message(message.channel,lang["charnotexist"].format(i.key))
    if command_check(prefix,message,'charset name',['charsetname','charset PV','charsetpv','charsetPV','charset pv','charset PM','charsetpm','charsetPM','charset pm',
                                                                         'charset force','charset strength','charset str','charsetstr','charset esprit','charset spirit','charset spr','charsetspr',
                                                                         'charset charisme','charset charisma','charset cha','charsetcha','charset agilite','charset furtivite','charset agi',
                                                                         'charset agility','charsetagi','charset lp','charsetlp','charset lightpt','charset dp','charsetdp','charset darkpt',
                                                                         'charset defaultmod','charsetdmod','charset dmod','charset defaultkarma','charsetdkar','charset dkar','charset intuition',
                                                                         'charset int','charsetint','charset HP','charset hp','charsetHP','charsethp','charset MP','charset mp','charsetMP',
                                                                         'charsetmp']) and chanMJ:#message.content.startswith(prefix+'charset') and chanMJ:
        char = jdr.get_character(get_args(prefix,message,'charset name',['charsetname','charset PV','charsetpv','charsetPV','charset pv','charset PM','charsetpm','charsetPM','charset pm',
                                                                         'charset force','charset strength','charset str','charsetstr','charset esprit','charset spirit','charset spr','charsetspr',
                                                                         'charset charisme','charset charisma','charset cha','charsetcha','charset agilite','charset furtivite','charset agi',
                                                                         'charset agility','charsetagi','charset lp','charsetlp','charset lightpt','charset dp','charsetdp','charset darkpt',
                                                                         'charset defaultmod','charsetdmod','charset dmod','charset defaultkarma','charsetdkar','charset dkar','charset intuition',
                                                                         'charset int','charsetint','charset HP','charset hp','charsetHP','charsethp','charset MP','charset mp','charsetMP',
                                                                         'charsetmp']).split(" ")[0])#message.content.split(" ")[2])
        if command_check(prefix,message,'charset name',['charsetname']):#message.content.startswith(prefix+'charset name'):
            ls = get_args(prefix,message,'charset name',['charsetname']).split(" ")#(message.content).split(" ")
            del(ls[0])
            nm = ""
            for i in ls:
                nm += i
                nm += " "
            char.setname(nm[:-1])
            yield from client.send_message(message.channel,lang["charset"].format(lang["name"]))
        elif command_check(prefix,message,'charset PV',['charsetpv','charsetPV','charset pv']):#message.content.startswith(prefix+'charset PV'):
            char = char.charset('pvmax',int(get_args(prefix,message,'charset PV',['charsetpv','charsetPV','charset pv','charset HP','charset hp','charsetHP','charsethp']).split(" ")[1]))
            yield from client.send_message(message.channel,lang["charset"].format(lang["PV"]+" max"))
        elif command_check(prefix,message,'charset PM',['charsetpm','charsetPM','charset pm']):#message.content.startswith(prefix+'charset PM'):
            char = char.charset('pmmax',int(get_args(prefix,message,'charset PM',['charsetpm','charsetPM','charset pm','charset MP','charset mp','charsetMP','charsetmp']).split(" ")[1]))
            yield from client.send_message(message.channel,lang["charset"].format(lang["PM"]+" max"))
        elif command_check(prefix,message,'charset force',['charset strength','charset str','charsetstr']):#message.content.startswith(prefix+'charset force'):
            char = char.charset('str',int(get_args(prefix,message,'charset force',['charset strength','charset str','charsetstr']).split(" ")[1]))
            yield from client.send_message(message.channel,lang["charset"].format(lang["force"]))
        elif command_check(prefix,message,'charset esprit',['charset spirit','charset spr','charsetspr']):#message.content.startswith(prefix+'charset esprit'):
            char = char.charset('spr',int(get_args(prefix,message,'charset esprit',['charset spirit','charset spr','charsetspr']).split(" ")[1]))
            yield from client.send_message(message.channel,lang["charset"].format(lang["esprit"]))
        elif command_check(prefix,message,'charset charisme',['charset charisma','charset cha','charsetcha']):#message.content.startswith(prefix+'charset charisme'):
            char = char.charset('cha',int(get_args(prefix,message,'charset charisme',['charset charisma','charset cha','charsetcha']).split(" ")[1]))
            yield from client.send_message(message.channel,lang["charset"].format(lang["charisme"]))
        elif command_check(prefix,message,'charset agilite',['charset furtivite','charset agi','charset agility','charsetagi']):#message.content.startswith(prefix+'charset furtivite') or message.content.startswith(prefix+'charset agilite'):
            char = char.charset('agi',int(get_args(prefix,message,'charset agilite',['charset furtivite','charset agi','charset agility','charsetagi']).split(" ")[1]))
            yield from client.send_message(message.channel,lang["charset"].format(lang["agilite"]))
        elif command_check(prefix,message,'charset lp',['charsetlp','charset lightpt']):#message.content.startswith(prefix+'charset lp'):
            if int(get_args(prefix,message,'charset lp',['charsetlp','charset lightpt']).split(" ")[1]) >= 0:
                char = char.charset('lp',int(get_args(prefix,message,'charset lp',['charsetlp','charset lightpt']).split(" ")[1]))
                yield from client.send_message(message.channel,lang["charset"].format("Light Points"))
        elif command_check(prefix,message,'charset dp',['charsetdp','charset darkpt']):#message.content.startswith(prefix+'charset dp'):
            if int(get_args(prefix,message,'charset dp',['charsetdp','charset darkpt']).split(" ")[1]) >= 0:
                char = char.charset('dp',int(get_args(prefix,message,'charset dp',['charsetdp','charset darkpt']).split(" ")[1]))
                yield from client.send_message(message.channel,lang["charset"].format("Dark Points"))
        elif command_check(prefix,message,'charset defaultmod',['charsetdmod','charset dmod']):#message.content.startswith(prefix+'charset defaultmod'):
            ndm = get_args(prefix,message,'charset defaultmod',['charsetdmod','charset dmod']).split(" ")[1]#(message.content).split(" ")[3]
            if ndm == "offensive" or ndm == "defensive":
                if ndm == "offensive": ndm = 0
                else: ndm = 1
                if ndm != char.default_mod:
                    char = char.switchmod(True)
                yield from client.send_message(message.channel,lang["charset"].format(lang["default"]+" "+lang["mod"]))
        elif command_check(prefix,message,'charset defaultkarma',['charsetdkar','charset dkar']):#message.content.startswith(prefix+'charset defaultkarma'):
            ndk = int(get_args(prefix,message,'charset defaultkarma',['charsetdkar','charset dkar']).split(" ")[1])
            if ndk >= -10 and ndk <= 10: char = char.charset('dkar',ndk)##char.default_karma = ndk
            yield from client.send_message(message.channel,lang["charset"].format(lang["default"]+" karma"))
        elif command_check(prefix,message,'charset intuition',['charset int','charsetint']):#message.content.startswith(prefix+'charset intuition'):
            val = int(get_args(prefix,message,'charset intuition',['charset int','charsetint']).split(" ")[1])
            if val >= 1 and val <= 6:
                char = char.charset('int',val)
                yield from client.send_message(message.channel,lang["charset"].format(lang["intuition"]))
    if command_check(prefix,message,'charset lore') and jdrchannel:#message.content.startswith(prefix+'charset lore'):
        if chanMJ:
            char = jdr.get_character(message.content.split(" ")[2])
        yield from client.send_message(message.channel,lang["write_lore"])
        lr = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel)
        if lr is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        char.setlore(lr.content)
        yield from client.send_message(message.channel,lang["charset"].format("lore"))
    if command_check(prefix,message,'chardmg',['chardamage']) and chanMJ:#message.content.startswith(prefix+'chardmg') and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        val = abs(int((message.content).split(" ")[2]))
        char = char.charset('pv',-val)
        embd = discord.Embed(title=char.name,description=lang["damaged"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["damage_taken"],value=str(val),inline=True)
        embd.add_field(name=lang["remaining_pv"],value=str(char.PV)+"/"+str(char.PVmax),inline=True)
        # if not char.check_life():
        #     embd.set_image(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/06/you-are-dead.png")
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'globaldmg',['globaldamage','gdmg','gdamage']) and chanMJ:#message.content.startswith(prefix+'globaldmg') and chanMJ:
        val = abs(int((message.content).split(" ")[1]))#replace(prefix+'globaldmg ',"")))
        embd = discord.Embed(title=lang["global_damage"],description=lang["damage_taken"]+" "+str(val),colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        deads = 0
        dead_ls = ""
        for i in charbase:
            if i.dead: continue
            i = i.charset('pv',-val)
            embd.add_field(name=i.name,value=str(i.PV)+" (-"+str(val)+")",inline=True)
            if not i.check_life():
                deads += 1
                dead_ls += (i.name+"\n")
        if deads > 0:
            embd.add_field(name=lang["dead_players"],value=dead_ls,inline=False)
        # if deads == len(charbase):
        #     embd.set_image(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/06/you-are-dead.png")
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'globalheal',['gheal']) and chanMJ:#message.content.startswith(prefix+'globalheal') and chanMJ:
        val = abs(int((message.content).split(" ")[1]))#replace(prefix+'globalheal ',"")))
        embd = discord.Embed(title=lang["global_heal"],description=lang["heal_amount"]+" "+str(val),colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        val2 = val
        for i in charbase:
            if i.dead: continue
            val = val2
            if i.PV+val2 > i.PVmax:
                val = i.PVmax-i.PV
            i = i.charset('pv',val)
            embd.add_field(name=i.name,value=str(i.PV)+" (+"+str(val)+")",inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'globalgetPM',['ggetPM','globalgetpm','ggetpm','globalgetMP','globalgetmp','ggetMP','ggetmp']) and chanMJ:
        val = int((message.content).split(" ")[1])#replace(prefix+'globalgetPM ',""))
        embd = discord.Embed(title=lang["global_pm"],description=lang["pm_earn"].format(str(val)),colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        val2 = val
        for i in charbase:
            if i.dead: continue
            val = val2
            if i.PM+val2 > i.PMmax:
                val = i.PMmax-i.PV
            if i.PM+val2 < 0:
                val = -i.PM
            i = i.charset('pm',val)
            sign = "+"
            if val < 0:
                sign = ""
            embd.add_field(name=i.name,value=str(i.PM)+" ("+sign+str(val)+")",inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'charheal',[]) and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        val = abs(int((message.content).split(" ")[2]))#replace(prefix+'charheal ',""))
        if char.PV+val > char.PVmax: val=char.PVmax-char.PV#char.PV = char.PVmax
        char = char.charset('pv',val)
        embd = discord.Embed(title=char.name,description=lang["healed"],colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["heal_amount"],value=str(val),inline=True)
        embd.add_field(name=lang["remaining_pv"],value=str(char.PV)+"/"+str(char.PVmax),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'getPM',['getpm','getMP','getmp']) and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        val = int((message.content).split(" ")[2])#replace(prefix+'getPM ',""))
        if char.PM + val < 0:
            yield from client.send_message(message.channel,lang["no_more_pm"].format(str(char.pm)))
            return
        else:
            if char.PM+val > char.PMmax: val=char.PMmax-char.PM#char.PM = char.PMmax
            char = char.charset('pm',val)
        got = lang["recovered"]
        if val < 0: got = lang["lost"]
        embd = discord.Embed(title=char.name,description=lang["get_pm"].format(got),colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["get_pm_amount"].format(got),value=str(abs(val)),inline=True)
        embd.add_field(name=lang["remaining_pm"],value=str(char.PM)+"/"+str(char.PMmax),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'setkarma',['addkarma','getkarma']) and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        val = int((message.content).split(" ")[2])#replace(prefix+'setkarma ',""))
        if Skill.isskillin(char.skills,7): val *= 2 #chanceux
        if Skill.isskillin(char.skills,84): #creature harmonieuse
            if char.karma == 0 and val < 0: val -= 5
            elif char.karma == 0 and val > 0: val +=5
            elif char.karma+val > -5 and char.karma+val < 5 and val < 0: val -= 9
            elif char.karma+val > -5 and char.karma+val < 5 and val > 0: val += 9
        if char.karma+val < -10: val=-10-char.karma#char.karma = -10
        if char.karma+val > 10: val=10-char.karma#char.karma = 10
        char = char.charset('kar',val)
        got = lang["recovered"]
        if val < 0: got = lang["lost"]
        embd = discord.Embed(title=char.name,description=lang["get_karma"].format(got),colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["get_karma_amount"].format(got),value=str(val),inline=True)
        embd.add_field(name=lang["current_karma"],value=str(char.karma),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'resetchar',['resetcharacter']) and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        char.resetchar()
        yield from client.send_message(message.channel,lang["resetchar"].format(char.name))
    if command_check(prefix,message,'pay',[]) and jdrchannel:
        val = abs(int((message.content).replace(prefix+'pay ',"")))
        if char.money-val < 0:
            yield from client.send_message(message.channel,lang["no_more_money"].format(char.money))
        else:
            char = char.charset('po',-val)
            embd = discord.Embed(title=char.name,description=lang["paid"],colour=discord.Color(int('ffff00',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            embd.add_field(name=lang["money_spent"],value=str(val),inline=True)
            embd.add_field(name=lang["remaining_money"],value=str(char.money),inline=True)
            yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'earnmoney',['earnpo','earnPO']) and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        val = abs(int((message.content).split(" ")[2]))#replace(prefix+'earnmoney ',""))
        char = char.charset('po',val)
        embd = discord.Embed(title=char.name,description=lang["earnmoney"],colour=discord.Color(int('ffff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["money_earned"],value=str(val),inline=True)
        embd.add_field(name=lang["remaining_money"],value=str(char.money),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'charinfo',['characterinfo']) and jdrchannel:
        if char.mod == 0: modd = lang["offensive"]
        else: modd = lang["defensive"]
        embd = discord.Embed(title=char.name,description="{} {}".format(char.race,char.classe),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        if char.dead: embd.set_image(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/06/you-are-dead.png")
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        if char.dead:
            embd.add_field(name=lang["PV"]+" :",value="DEAD",inline=True)
        else:
            embd.add_field(name=lang["PV"]+" :",value=str(char.PV)+"/"+str(char.PVmax),inline=True)
        if not char.dead: embd.add_field(name=lang["PM"]+" :",value=str(char.PM)+"/"+str(char.PMmax),inline=True)
        embd.add_field(name=lang["lvl"].capitalize()+" :",value=str(char.lvl),inline=True)
        if not char.dead: embd.add_field(name=lang["intuition"].capitalize()+" :",value=str(char.intuition),inline=True)
        if not char.dead: embd.add_field(name=lang["force"].capitalize()+" :",value=str(char.force),inline=True)
        if not char.dead: embd.add_field(name=lang["esprit"].capitalize()+" :",value=str(char.esprit),inline=True)
        if not char.dead: embd.add_field(name=lang["charisme"].capitalize()+" :",value=str(char.charisme),inline=True)
        if not char.dead: embd.add_field(name=lang["agilite"].capitalize()+" :",value=str(char.furtivite),inline=True)
        if not char.dead: embd.add_field(name=lang["karma"].capitalize()+" :",value=str(char.karma),inline=True)
        embd.add_field(name=lang["money"].capitalize()+" :",value=str(char.money),inline=True)
        if not char.dead: embd.add_field(name=lang["lp"]+" :",value=str(char.lp),inline=True)
        if not char.dead: embd.add_field(name=lang["dp"]+" :",value=str(char.dp),inline=True)
        if not char.dead: embd.add_field(name=lang["mod"].capitalize()+" :",value=modd,inline=True)
        embd.add_field(name=lang["mental"].capitalize()+" :",value=str(char.mental),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'map') and chanMJ:
        if command_check(prefix,message,'map clearall',['map clrall','map reset']):
            Map.clear(jdr.server,jdr.channel)
            yield from client.send_message(message.channel,lang["mapreset"])
        elif command_check(prefix,message,'map show'):
            dim = get_args(prefix,message,'map show')
            mp = Map(int(dim.split(" ")[0]),int(dim.split(" ")[1]),jdr.server,jdr.channel)
            yield from mp.send(client,message.channel)
        elif command_check(prefix,message,'map token',['map tk']):
            if command_check(prefix,message,'map token add',['map tk add','map token +','map tk +']):
                tk = Token(get_args(prefix,message,'map token add',['map tk add','map token +','map tk +']),jdr.server,jdr.channel)
                tk.save()
                yield from client.send_message(message.channel,lang["tokenadd"].format(tk.name))
            elif command_check(prefix,message,'map token remove',['map tk rm','map token rm','map tk remove','map token -','map tk -']):
                tkname = get_args(prefix,message,'map token remove',['map tk rm','map token rm','map tk remove','map token -','map tk -'])
                try: tk = Token.load(tkname,jdr.server,jdr.channel)
                except:
                    yield from client.send_message(message.channel,lang["token_notexist"].format(tkname))
                    return
                tk.remove()
                yield from client.send_message(message.channel,lang["tokenrm"].format(tkname))
            elif command_check(prefix,message,'map token move',['map tk move']):
                args = get_args(prefix,message,'map token move',['map tk move']).split(" ")
                while "" in args: args.remove("")
                tkname = args[0]
                try: tk = Token.load(tkname,jdr.server,jdr.channel)
                except:
                    yield from client.send_message(message.channel,lang["token_notexist"].format(tkname))
                    return
                dz = 0
                if len(args) > 3: dz = int(args[3])
                tk.move(int(args[1]),int(args[2]),dz)
                yield from client.send_message(message.channel,lang["tokenmove"].format(tkname,tk.x,tk.y,tk.z))
        elif command_check(prefix,message,'map effect'):
            if command_check(prefix,message,'map effect add',['map effect +']):
                args = get_args(prefix,message,'map effect add',['map effect +'])
                parameters = {}
                if "{" in args and "}" in args:
                    parameters = reformatAreaParameters(args[args.find("{"):args.find("}")+1])
                args = args.split(" ")
                while "" in args: args.remove("")
                tkname = args[0]
                try: tk = Token.load(tkname,jdr.server,jdr.channel)
                except:
                    yield from client.send_message(message.channel,lang["token_notexist"].format(tkname))
                    return
                if args[4].lower() == "sphere":
                    shape = Shape.SPHERE
                elif args[4].lower() == "line":
                    shape = Shape.LINE
                elif args[4].lower() == "rect":
                    shape = Shape.RECT
                elif args[4].lower() == "cube":
                    shape = Shape.CUBE
                elif args[4].lower() == "conic":
                    shape = Shape.CONIC
                else:
                    shape = Shape.CIRCLE
                try: tk.spawnAreaEffect(int(args[1]),int(args[2]),int(args[3]),shape,parameters)
                except:
                    yield from client.send_message(message.channel,lang["effet_parse_error"])
                    return
                tk.registerEffect(int(args[1]),int(args[2]),int(args[3]),shape,parameters)
                yield from client.send_message(message.channel,lang["effect_register"].format(tkname))
            if command_check(prefix,message,'map effect clear'):
                tkname = get_args(prefix,message,'map effect clear')
                try: tk = Token.load(tkname,jdr.server,jdr.channel)
                except:
                    yield from client.send_message(message.channel,lang["token_notexist"].format(tkname))
                    return
                tk.cleareffect()
                yield from client.send_message(message.channel,lang["token_clear"].format(tkname))
        else:
            f = open("mapmonde.png","rb")
            yield from client.send_file(message.channel,f)
            f.close()
    if command_check(prefix,message,'stat',['charstat','characterstat']) and jdrchannel:
        embd = discord.Embed(title=lang["stat"],description=char.name,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["dice_rolled"],value=str(char.stat[0]),inline=True)
        embd.add_field(name=lang["super_critic_success"],value=str(char.stat[1]),inline=True)
        embd.add_field(name=lang["critic_success"],value=str(char.stat[2]),inline=True)
        embd.add_field(name=lang["success"],value=str(char.stat[3]),inline=True)
        embd.add_field(name=lang["fail"],value=str(char.stat[4]),inline=True)
        embd.add_field(name=lang["critic_fail"],value=str(char.stat[5]),inline=True)
        embd.add_field(name=lang["super_critic_fail"],value=str(char.stat[6]),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'globalstat',['gstat']) and jdrchannel:
        ls = [0,0,0,0,0,0,0]
        for i in charbase:
            ls = sum_ls(ls,i.stat)
        embd = discord.Embed(title=lang["stat"],description=lang["stat_all"],colour=discord.Color(randint(0,int('ffffff',16))))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["dice_rolled"],value=str(ls[0]),inline=True)
        embd.add_field(name=lang["super_critic_success"],value=str(ls[1]),inline=True)
        embd.add_field(name=lang["critic_success"],value=str(ls[2]),inline=True)
        embd.add_field(name=lang["success"],value=str(ls[3]),inline=True)
        embd.add_field(name=lang["fail"],value=str(ls[4]),inline=True)
        embd.add_field(name=lang["critic_fail"],value=str(ls[5]),inline=True)
        embd.add_field(name=lang["super_critic_fail"],value=str(ls[6]),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'use') and jdrchannel:
        if char.dead:
            yield from client.send_message(message.channel,lang["is_dead"].format(char.name))
            return
        if command_check(prefix,message,'use lightpt',['use lp','use lightpoint']):
            if char.lp <= 0:
                yield from client.send_message(message.channel,lang["no_more_lp"])
            else:
                yield from client.send_message(message.channel,lang["used_lp"].format(char.name))
                char.uselp()
                result = randint(1,6)
                yield from client.send_message(message.channel,lang["result_test_nomax"].format(lang["chance"],str(result)))
                if result == 1: yield from client.send_message(message.channel,lang["chance_1"])
                elif result == 2: yield from client.send_message(message.channel,lang["chance_2"])
                elif result == 3: yield from client.send_message(message.channel,lang["chance_3"])
                elif result == 4: yield from client.send_message(message.channel,lang["chance_4"])
                elif result == 5: yield from client.send_message(message.channel,lang["chance_5"])
                elif result == 6: yield from client.send_message(message.channel,lang["chance_1"])
        elif command_check(prefix,message,'use darkpt',['use dp','use darkpoint']):
            if char.dp <= 0:
                yield from client.send_message(message.channel,lang["no_more_dp"])
            else:
                yield from client.send_message(message.channel,lang["used_dp"].format(char.name))
                char.usedp()
                result = randint(1,6)
                yield from client.send_message(message.channel,lang["result_test_nomax"].format(lang["malchance"],str(result)))
                if result == 1: yield from client.send_message(message.channel,lang["malchance_1"])
                elif result == 2: yield from client.send_message(message.channel,lang["malchance_2"])
                elif result == 3: yield from client.send_message(message.channel,lang["malchance_3"])
                elif result == 4: yield from client.send_message(message.channel,lang["malchance_4"])
                elif result == 5: yield from client.send_message(message.channel,lang["malchance_5"])
                elif result == 6: yield from client.send_message(message.channel,lang["malchance_1"])
        else:
            itname = get_args(prefix,message,'use')
            for i in char.inventory.items.keys():
                if i.name == itname:
                    char.inventory -= i
                    yield from client.send_message(message.channel,lang["used_item"].format(char.name,i.name))
                    return
            yield from client.send_message(message.channel,lang["no_more_item"])
    if command_check(prefix,message,'switchmod',['switchmode']) and jdrchannel:
        char = char.switchmod()
        if char.mod == 1:
            yield from client.send_message(message.channel,lang["switchmod"].format(char.name,lang["defensive"]))
        else:
            yield from client.send_message(message.channel,lang["switchmod"].format(char.name,lang["offensive"]))
    if command_check(prefix,message,'setmental',[]) and jdrchannel:
        if char.dead:
            yield from client.send_message(message.channel,lang["is_dead"].format(char.name))
            return
        msg = message.content.replace(prefix+'setmental ',"")
        if "+" in message.content:
            msg = msg.replace("+","")
            got = lang["recovered"]
            char = char.charset('ment',char.mental+int(msg))
        elif "-" in message.content:
            msg = msg.replace("-","")
            got = lang["lost"]
            char = char.charset('ment',char.mental-int(msg))
        else:
            got = lang["new_value"]
            char = char.charset('ment',int(msg))
        embd = discord.Embed(title=char.name,description=lang["setmental"].format(got),colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        if "+" in message.content or "-" in message.content: embd.add_field(name=lang["mental_amount"].format(got),value=msg,inline=True)
        embd.add_field(name=lang["current_mental"],value=str(char.mental),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'lvlup',['levelup']) and jdrchannel and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        char.lvlup()
        embd = discord.Embed(title=char.name,description=lang["lvlup"],colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["lvl"].capitalize()+" :",value=str(char.lvl),inline=True)
        if char.lvl == 2:
            dice,dice2 = randint(1,10),randint(1,10)
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_2"].format(str(dice),str(dice2)),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["force"]),value=str(char.force),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["esprit"]),value=str(char.esprit),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["charisme"]),value=str(char.charisme),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["agilite"]),value=str(char.furtivite),inline=True)
        elif char.lvl == 3:
            dice = randint(1,10)
            dic = {"force":char.force,"esprit":char.esprit,"charisme":char.charisme,"agilite":char.furtivite}
            statmin = ("force",char.force)
            for i,k in dic.items():
                if k < statmin[1]: statmin = (i,k)
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_3"].format(statmin[0],str(dice)),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang[statmin[0]]),value=str(statmin[1]),inline=True)
            embd.add_field(name=lang["lvlup_next"].format(lang[statmin[0]]),value=str(statmin[1]+dice),inline=True)
        elif char.lvl == 4:
            dice = randint(1,100)
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_4"].format(str(dice)),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PV"]),value=str(char.PV)+"/"+str(char.PVmax),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PM"]),value=str(char.PM)+"/"+str(char.PMmax),inline=True)
        elif char.lvl == 5:
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_5"],inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["force"]),value=str(char.force),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["esprit"]),value=str(char.esprit),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["charisme"]),value=str(char.charisme),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["agilite"]),value=str(char.furtivite),inline=True)
        else:
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_6"],inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PV"]),value=str(char.PV)+"/"+str(char.PVmax),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PM"]),value=str(char.PM)+"/"+str(char.PMmax),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["force"]),value=str(char.force),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["esprit"]),value=str(char.esprit),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["charisme"]),value=str(char.charisme),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["agilite"]),value=str(char.furtivite),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'inventory',['inv']) and jdrchannel:
        if command_check(prefix,message,'inventory add',['inv add']) and chanMJ:
            char = jdr.get_character(message.content.split(" ")[2])
            qte = 1
            if len(message.content.split(" ")) > 4: qte = abs(int(message.content.split(" ")[4]))
            item = Item.find(message.content.split(" ")[3].replace("_"," "))
            if item is None:
                yield from client.send_message(message.channel,lang["unexisting_item"])
            elif char.inventory.weight + (item.weight*qte) > char.inventory.maxweight:
                yield from client.send_message(message.channel,lang["inv_full"])
            else:
                char.inventory.additem(item,qte)
                yield from client.send_message(message.channel,lang["inv_add"])
        elif command_check(prefix,message,'inventory delete',['inv delete','inventory del','inv del']) and chanMJ:
            char = jdr.get_character(message.content.split(" ")[2])
            qte = 1
            if len(message.content.split(" ")) > 4: qte = abs(int(message.content.split(" ")[4]))
            item = Item.find(message.content.split(" ")[3].replace("_"," "))
            keyitem = None
            for i in char.inventory.items.keys():
                if i.ID == item.ID:
                    keyitem = i
                    break
            if item is None:
                yield from client.send_message(message.channel,lang["unexisting_item"])
            elif keyitem is None:
                yield from client.send_message(message.channel,lang["item_not_found"])
            else:
                qte = min(qte,char.inventory.items[keyitem])
                char.inventory.rmitem(item,qte)
                yield from client.send_message(message.channel,lang["inv_rm"])
        else:
            embd = discord.Embed(title=char.name,description=lang["inv"].format(str(char.inventory.weight),str(char.inventory.maxweight)),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            for i,k in char.inventory.items.items():
                itstr = lang["inv_item"].format(str(k),str(i.weight))
                embd.add_field(name=i.name,value=itstr,inline=True)
            yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petadd',['pet+']) and jdrchannel and chanMJ:
        char = jdr.get_character(get_args(prefix,message,'petadd',['pet+']).split(" ")[0])
        if char.pet_add(get_args(prefix,message,'petadd',['pet+']).split(" ")[1]):
            yield from client.send_message(message.channel,lang["petadd"].format(get_args(prefix,message,'petadd',['pet+']).split(" ")[1],char.name))
        else:
            yield from client.send_message(message.channel,lang["petexist"].format(get_args(prefix,message,'petadd',['pet+']).split(" ")[1]))
    if command_check(prefix,message,'petremove',['pet-']) and jdrchannel and chanMJ:
        char = jdr.get_character(get_args(prefix,message,'petremove',['pet-']).split(" ")[0])
        if char.pet_delete(get_args(prefix,message,'petremove',['pet-']).split(" ")[1]):
            yield from client.send_message(message.channel,lang["petrm"].format(get_args(prefix,message,'petremove',['pet-']).split(" ")[1],char.name))
        else:
            yield from client.send_message(message.channel,lang["petnotfound"].format(get_args(prefix,message,'petremove',['pet-']).split(" ")[1]))
    if command_check(prefix,message,'petset name',['petsetname','petset PV','petsetpv','petsetPV','petset pv','petset PM','petsetpm','petsetPM','petset pm','petset force','petset strength',
                                                   'petset str','petsetstr','petset esprit','petset spirit','petset spr','petsetspr','petset charisme','petset charisma','petset cha','petsetcha',
                                                   'petset agilite','petset furtivite','petset agi','petset agility','petsetagi','petset defaultmod','petsetdmod','petset dmod','petset intuition',
                                                   'petset int','petsetint','petset espece','petset species','petset spe']) and jdrchannel and chanMJ:
        temp = get_args(prefix,message,'petset name',['petsetname','petset PV','petsetpv','petsetPV','petset pv','petset PM','petsetpm','petsetPM','petset pm','petset force','petset strength',
                                                   'petset str','petsetstr','petset esprit','petset spirit','petset spr','petsetspr','petset charisme','petset charisma','petset cha','petsetcha',
                                                   'petset agilite','petset furtivite','petset agi','petset agility','petsetagi','petset defaultmod','petsetdmod','petset dmod','petset intuition',
                                                   'petset int','petsetint','petset espece','petset species','petset spe']).split(" ")
        char = jdr.get_character(temp[0])
        pet = temp[1]
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        if command_check(prefix,message,'petset name',['petsetname']):#message.content.startswith(prefix+'charset name'):
            ls = get_args(prefix,message,'petset name',['petsetname']).split(" ")#(message.content).split(" ")
            del(ls[0])
            del(ls[0])
            nm = ""
            for i in ls:
                nm += i
                nm += " "
            char.pet[pet].setname(nm[:-1])
            yield from client.send_message(message.channel,lang["petset"].format(lang["name"]))
        elif command_check(prefix,message,'petset PV',['petsetpv','petsetPV','petset pv']):#message.content.startswith(prefix+'charset PV'):
            char = char.pet[pet].petset('pvmax',int(temp[2]))
            yield from client.send_message(message.channel,lang["petset"].format(lang["PV"]+" max"))
        elif command_check(prefix,message,'petset PM',['petsetpm','petsetPM','petset pm']):#message.content.startswith(prefix+'charset PM'):
            char = char.pet[pet].petset('pmmax',int(temp[2]))
            yield from client.send_message(message.channel,lang["petset"].format(lang["PM"]+" max"))
        elif command_check(prefix,message,'petset force',['petset strength','petset str','petsetstr']):#message.content.startswith(prefix+'charset force'):
            char = char.pet[pet].petset('str',int(temp[2]))
            yield from client.send_message(message.channel,lang["petset"].format(lang["force"]))
        elif command_check(prefix,message,'petset esprit',['petset spirit','petset spr','petsetspr']):#message.content.startswith(prefix+'charset esprit'):
            char = char.pet[pet].petset('spr',int(temp[2]))
            yield from client.send_message(message.channel,lang["petset"].format(lang["esprit"]))
        elif command_check(prefix,message,'petset charisme',['petset charisma','petset cha','petsetcha']):#message.content.startswith(prefix+'charset charisme'):
            char = char.pet[pet].petset('cha',int(temp[2]))
            yield from client.send_message(message.channel,lang["petset"].format(lang["charisme"]))
        elif command_check(prefix,message,'petset agilite',['petset furtivite','petset agi','petset agility','petsetagi']):#message.content.startswith(prefix+'charset furtivite') or message.content.startswith(prefix+'charset agilite'):
            char = char.pet[pet].petset('agi',int(temp[2]))
            yield from client.send_message(message.channel,lang["petset"].format(lang["agilite"]))
        elif command_check(prefix,message,'petset defaultmod',['petsetdmod','petset dmod']):#message.content.startswith(prefix+'charset defaultmod'):
            ndm = temp[2]
            if ndm == "offensive" or ndm == "defensive":
                if ndm == "offensive": ndm = 0
                else: ndm = 1
                if ndm != char.pet[pet].default_mod:
                    char = char.pet[pet].switchmod(True)
                yield from client.send_message(message.channel,lang["petset"].format(lang["default"]+" "+lang["mod"]))
        elif command_check(prefix,message,'petset instinct',['petset int','petsetint']):#message.content.startswith(prefix+'charset intuition'):
            val = int(temp[2])
            if val >= 1 and val <= 6:
                char = char.pet[pet].petset('int',val)
                yield from client.send_message(message.channel,lang["petset"].format(lang["instinct"]))
        elif command_check(prefix,message,'petset espece',['petset species','petset spe']):
            ls = get_args(prefix,message,'petset espece',['petset species','petset spe']).split(" ")#(message.content).split(" ")
            del(ls[0])
            del(ls[0])
            nm = ""
            for i in ls:
                nm += i
                nm += " "
            char.pet[pet].setespece(nm[:-1])
            yield from client.send_message(message.channel,lang["petset"].format(lang["espece"]))
    if command_check(prefix,message,'petswitchmod') and jdrchannel:
        if get_args(prefix,message,'petswitchmod') not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(get_args(prefix,message,'petswitchmod')))
            return
        char = char.pet[get_args(prefix,message,'petswitchmod')].switchmod()
        if char.pet[get_args(prefix,message,'petswitchmod')].mod == 0: mod = lang["offensive"]
        else: mod = lang["defensive"]
        yield from client.send_message(message.channel,lang["switchmod"].format(get_args(prefix,message,'petswitchmod'),mod))
    if command_check(prefix,message,'petlvlup') and jdrchannel and chanMJ:
        char = jdr.get_character(get_args(prefix,message,'petlvlup').split(" ")[0])
        if get_args(prefix,message,'petlvlup').split(" ")[1] not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(get_args(prefix,message,'petlvlup').split(" ")[1]))
            return
        char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].lvlup()
        embd = discord.Embed(title=char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].name,description=lang["lvlup"],colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["lvl"].capitalize()+" :",value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].lvl),inline=True)
        if char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].lvl == 2:
            dice,dice2 = randint(1,10),randint(1,10)
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_2"].format(str(dice),str(dice2)),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["force"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].force),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["esprit"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].esprit),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["charisme"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].charisme),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["agilite"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].agilite),inline=True)
        elif char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].lvl == 3:
            dice = randint(1,10)
            dic = {"force":char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].force,"esprit":char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].esprit,
                   "charisme":char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].charisme,"agilite":char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].agilite}
            statmin = ("force",char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].force)
            for i,k in dic.items():
                if k < statmin[1]: statmin = (i,k)
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_3"].format(statmin[0],str(dice)),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang[statmin[0]]),value=str(statmin[1]),inline=True)
            embd.add_field(name=lang["lvlup_next"].format(lang[statmin[0]]),value=str(statmin[1]+dice),inline=True)
        elif char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].lvl == 4:
            dice = randint(1,100)
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_4"].format(str(dice)),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PV"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PV)+"/"+str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PVmax),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PM"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PM)+"/"+str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PMmax),inline=True)
        elif char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].lvl == 5:
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_5"],inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["force"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].force),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["esprit"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].esprit),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["charisme"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].charisme),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["agilite"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].agilite),inline=True)
        else:
            embd.add_field(name=lang["lvlup_bonus"],value=lang["lvlup_6"],inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PV"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PV)+"/"+str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PVmax),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["PM"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PM)+"/"+str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].PMmax),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["force"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].force),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["esprit"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].esprit),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["charisme"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].charisme),inline=True)
            embd.add_field(name=lang["lvlup_current"].format(lang["agilite"]),value=str(char.pet[get_args(prefix,message,'petlvlup').split(" ")[1]].agilite),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petroll') and jdrchannel:#message.content.startswith(prefix+'roll') and jdrchannel:
        field = (message.content).replace(prefix+'petroll ',"")
        pet = field.split(" ")[0]
        field = field.replace(pet+" ","")
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
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
        yield from char.pet[pet].roll(client,message.channel,lang,msg,modifier)
    if command_check(prefix,message,'petinfo') and jdrchannel:
        pet = get_args(prefix,message,'petinfo')
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        if char.pet[pet].mod == 0: modd = lang["offensive"]
        else: modd = lang["defensive"]
        embd = discord.Embed(title=char.pet[pet].name,description=lang["petbelong"].format(char.pet[pet].espece,char.name),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["PV"]+" :",value=str(char.pet[pet].PV)+"/"+str(char.pet[pet].PVmax),inline=True)
        embd.add_field(name=lang["PM"]+" :",value=str(char.pet[pet].PM)+"/"+str(char.pet[pet].PMmax),inline=True)
        embd.add_field(name=lang["lvl"].capitalize()+" :",value=str(char.pet[pet].lvl),inline=True)
        embd.add_field(name=lang["instinct"].capitalize()+" :",value=str(char.pet[pet].instinct),inline=True)
        embd.add_field(name=lang["force"].capitalize()+" :",value=str(char.pet[pet].force),inline=True)
        embd.add_field(name=lang["esprit"].capitalize()+" :",value=str(char.pet[pet].esprit),inline=True)
        embd.add_field(name=lang["charisme"].capitalize()+" :",value=str(char.pet[pet].charisme),inline=True)
        embd.add_field(name=lang["agilite"].capitalize()+" :",value=str(char.pet[pet].agilite),inline=True)
        embd.add_field(name=lang["karma"].capitalize()+" :",value=str(char.pet[pet].karma),inline=True)
        embd.add_field(name=lang["mod"].capitalize()+" :",value=modd,inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petsetkarma',['petkarma']) and jdrchannel and chanMJ:
        char = jdr.get_character(get_args(prefix,message,'petsetkarma',['petkarma']).split(" ")[0])
        pet = get_args(prefix,message,'petsetkarma',['petkarma']).split(" ")[1]
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        val = int(get_args(prefix,message,'petsetkarma',['petkarma']).split(" ")[2])
        char = char.pet[pet].petset('kar',val)
        got = lang["recovered"]
        if val < 0: got = lang["lost"]
        embd = discord.Embed(title=char.pet[pet].name,description=lang["get_karma"].format(got),colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["get_karma_amount"].format(got),value=str(val),inline=True)
        embd.add_field(name=lang["current_karma"],value=str(char.pet[pet].karma),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petstat') and jdrchannel:
        pet = get_args(prefix,message,'petstat')
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        embd = discord.Embed(title=lang["petstat"],description=char.pet[pet].name,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["dice_rolled"],value=str(char.pet[pet].stat[0]),inline=True)
        embd.add_field(name=lang["super_critic_success"],value=str(char.pet[pet].stat[1]),inline=True)
        embd.add_field(name=lang["critic_success"],value=str(char.pet[pet].stat[2]),inline=True)
        embd.add_field(name=lang["success"],value=str(char.pet[pet].stat[3]),inline=True)
        embd.add_field(name=lang["fail"],value=str(char.pet[pet].stat[4]),inline=True)
        embd.add_field(name=lang["critic_fail"],value=str(char.pet[pet].stat[5]),inline=True)
        embd.add_field(name=lang["super_critic_fail"],value=str(char.pet[pet].stat[6]),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petdmg',['petdamage']) and jdrchannel and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        pet = message.content.split(" ")[2]
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        val = abs(int((message.content).split(" ")[3]))
        char = char.pet[pet].petset('pv',-val)
        embd = discord.Embed(title=char.pet[pet].name,description=lang["damaged"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["damage_taken"],value=str(val),inline=True)
        embd.add_field(name=lang["remaining_pv"],value=str(char.pet[pet].PV)+"/"+str(char.pet[pet].PVmax),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petheal',['petcure']) and jdrchannel and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        pet = message.content.split(" ")[2]
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        val = abs(int((message.content).split(" ")[3]))#replace(prefix+'charheal ',""))
        if char.pet[pet].PV+val > char.pet[pet].PVmax: val=char.pet[pet].PVmax-char.pet[pet].PV#char.PV = char.PVmax
        char = char.pet[pet].petset('pv',val)
        embd = discord.Embed(title=char.pet[pet].name,description=lang["healed"],colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["heal_amount"],value=str(val),inline=True)
        embd.add_field(name=lang["remaining_pv"],value=str(char.pet[pet].PV)+"/"+str(char.pet[pet].PVmax),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'petgetPM',['petgetpm','petgetMP','petgetmp','petpm','petPM','petmp','petMP']) and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        pet = message.content.split(" ")[2]
        if pet not in char.pet:
            yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
            return
        val = int((message.content).split(" ")[3])#replace(prefix+'getPM ',""))
        if char.pet[pet].PM + val < 0:
            yield from client.send_message(message.channel,lang["no_more_pm"].format(str(char.pet[pet].PM)))
            return
        else:
            if char.pet[pet].PM+val > char.pet[pet].PMmax: val=char.pet[pet].PMmax-char.pet[pet].PM#char.PM = char.PMmax
            char = char.pet[pet].petset('pm',val)
        got = lang["recovered"]
        if val < 0: got = lang["lost"]
        embd = discord.Embed(title=char.pet[pet].name,description=lang["get_pm"].format(got),colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["get_pm_amount"].format(got),value=str(abs(val)),inline=True)
        embd.add_field(name=lang["remaining_pm"],value=str(char.pet[pet].PM)+"/"+str(char.pet[pet].PMmax),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'kill',['characterkill','charkill']) and chanMJ:
        char = jdr.get_character(get_args(prefix,message,'kill',['characterkill','charkill']))
        yield from client.send_message(message.channel,lang["kill_confirm"].format(char.name))
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        char.kill()
        char.unlink()
        f = open("you are dead.png","rb")
        yield from client.send_file(message.channel,f,content=lang["killed"].format(char.name))
        f.close()
    if command_check(prefix,message,'skillinfo',['skinfo']) and jdrchannel:
        sklist = get_args(prefix,message,'skillinfo',['skinfo']).split("|")
        ls = []
        for i in sklist:
            ls += Skill.skillsearch(i)
        descr = str(sklist)
        descr = descr.replace("[","")
        descr = descr.replace("]","")
        embd = discord.Embed(title=lang["skillsearch"],description=descr,colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for i in ls:
            embd.add_field(name="{}#{} ({})".format(i.ID,i.name,i.origine),value=i.description.replace("\\n","\n"),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'skill',['sk','charskill','charsk']) and jdrchannel:
        embd = discord.Embed(title=char.name,description=lang["sklist"],colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for i in char.skills:
            embd.add_field(name="{}#{} ({})".format(i.ID,i.name,i.origine),value=i.description.replace("\\n","\n"),inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'skillassign',['skassign']) and chanMJ:
        args = get_args(prefix,message,'skillassign',['skassign']).split(" ")
        char = jdr.get_character(args[0])
        sk = Skill(int(args[1]))
        char.assign_skill(sk)
        yield from client.send_message(message.channel,lang["assign_skill"].format(sk.name,char.name))
    if command_check(prefix,message,'mjcharinfo',['MJcharinfo','mjcharacterinfo','MJcharacterinfo','mjswitchmod','MJswitchmod','mjswitchmode','MJswitchmode',
                                                  'mjpay','MJpay','mjsetmental','MJsetmental','mjroll','MJroll','mjinventory','MJinventory','mjinv','MJinv',
                                                  'mjpetroll','MJpetroll','mjpetinfo','MJpetinfo','MJpetswitchmod','mjpetswitchmod']) and jdrchannel and chanMJ:
        char = jdr.get_character(message.content.split(" ")[1])
        if command_check(prefix,message,'mjcharinfo',['MJcharinfo','mjcharacterinfo','MJcharacterinfo']):
            if char.mod == 0: modd = lang["offensive"]
            else: modd = lang["defensive"]
            embd = discord.Embed(title=char.name,description="{} {}".format(char.race,char.classe),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            if char.dead: embd.set_image(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/06/you-are-dead.png")
            if char.dead:
                embd.add_field(name=lang["PV"]+" :",value="DEAD",inline=True)
            else:
                embd.add_field(name=lang["PV"]+" :",value=str(char.PV)+"/"+str(char.PVmax),inline=True)
            if not char.dead: embd.add_field(name=lang["PM"]+" :",value=str(char.PM)+"/"+str(char.PMmax),inline=True)
            embd.add_field(name=lang["lvl"].capitalize()+" :",value=str(char.lvl),inline=True)
            if not char.dead: embd.add_field(name=lang["intuition"].capitalize()+" :",value=str(char.intuition),inline=True)
            if not char.dead: embd.add_field(name=lang["force"].capitalize()+" :",value=str(char.force),inline=True)
            if not char.dead: embd.add_field(name=lang["esprit"].capitalize()+" :",value=str(char.esprit),inline=True)
            if not char.dead: embd.add_field(name=lang["charisme"].capitalize()+" :",value=str(char.charisme),inline=True)
            if not char.dead: embd.add_field(name=lang["agilite"].capitalize()+" :",value=str(char.furtivite),inline=True)
            if not char.dead: embd.add_field(name=lang["karma"].capitalize()+" :",value=str(char.karma),inline=True)
            embd.add_field(name=lang["money"].capitalize()+" :",value=str(char.money),inline=True)
            if not char.dead: embd.add_field(name=lang["lp"]+" :",value=str(char.lp),inline=True)
            if not char.dead: embd.add_field(name=lang["dp"]+" :",value=str(char.dp),inline=True)
            if not char.dead: embd.add_field(name=lang["mod"].capitalize()+" :",value=modd,inline=True)
            embd.add_field(name=lang["mental"].capitalize()+" :",value=str(char.mental),inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if command_check(prefix,message,'mjinventory',['MJinventory','mjinv','MJinv']):
            embd = discord.Embed(title=char.name,description=lang["inv"].format(str(char.inventory.weight),str(char.inventory.maxweight)),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            for i,k in char.inventory.items.items():
                itstr = lang["inv_item"].format(str(k),str(i.weight))
                embd.add_field(name=i.name,value=itstr,inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if command_check(prefix,message,'mjswitchmod',['MJswitchmod','mjswitchmode','MJswitchmode']):
            char = char.switchmod()
            if char.mod == 1:
                yield from client.send_message(message.channel,lang["switchmod"].format(char.name,lang["defensive"]))
            else:
                yield from client.send_message(message.channel,lang["switchmod"].format(char.name,lang["offensive"]))
        if command_check(prefix,message,'mjpay',['MJpay']):
            val = abs(int(message.content.split(" ")[2]))
            if char.money-val < 0:
                yield from client.send_message(message.channel,lang["no_more_money"].format(char.money))
            else:
                char = char.charset('po',-val)
                embd = discord.Embed(title=char.name,description=lang["paid"],colour=discord.Color(int('ffff00',16)))
                embd.set_footer(text="The Tale of Great Cosmos")
                embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
                embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
                embd.add_field(name=lang["money_spent"],value=str(val),inline=True)
                embd.add_field(name=lang["remaining_money"],value=str(char.money),inline=True)
                yield from client.send_message(message.channel,embed=embd)
        if command_check(prefix,message,'mjsetmental',['MJsetmental']):
            msg = message.content.replace(message.content.split(" ")[0]+" "+message.content.split(" ")[1],"")#message.content.split(" ")[2]
            if "+" in message.content:
                msg = msg.replace("+","")
                got = lang["recovered"]
                char = char.charset('ment',char.mental+int(msg))
            elif "-" in message.content:
                msg = msg.replace("-","")
                got = lang["lost"]
                char = char.charset('ment',char.mental-int(msg))
            else:
                got = lang["new_value"]
                char = char.charset('ment',int(msg))
            embd = discord.Embed(title=char.name,description=lang["setmental"].format(got),colour=discord.Color(int('5B005B',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            if "+" in message.content or "-" in message.content: embd.add_field(name=lang["mental_amount"].format(got),value=msg,inline=True)
            embd.add_field(name=lang["current_mental"],value=str(char.mental),inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if command_check(prefix,message,'mjroll',['MJroll']):
            field = (message.content).replace(message.content.split(" ")[0]+" "+message.content.split(" ")[1],"")
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
            yield from char.roll(client,message.channel,lang,msg,modifier)
        if command_check(prefix,message,'MJpetroll',['mjpetroll']):
            field = (message.content).replace(message.content.split(" ")[0]+" "+message.content.split(" ")[1]+" ","")
            pet = field.split(" ")[0]
            field = field.replace(pet+" ","")
            if pet not in char.pet:
                yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
                return
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
            yield from char.pet[pet].roll(client,message.channel,lang,msg,modifier)
        if command_check(prefix,message,'MJpetinfo',['mjpetinfo']):
            pet = get_args(prefix,message,'mjpetinfo',['mjpetinfo']).split(" ")[1]
            if pet not in char.pet:
                yield from client.send_message(message.channel,lang["petnotfound"].format(pet))
                return
            if char.pet[pet].mod == 0: modd = lang["offensive"]
            else: modd = lang["defensive"]
            embd = discord.Embed(title=char.pet[pet].name,description=lang["petbelong"].format(char.pet[pet].espece,char.name),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            embd.add_field(name=lang["PV"]+" :",value=str(char.pet[pet].PV)+"/"+str(char.pet[pet].PVmax),inline=True)
            embd.add_field(name=lang["PM"]+" :",value=str(char.pet[pet].PM)+"/"+str(char.pet[pet].PMmax),inline=True)
            embd.add_field(name=lang["lvl"].capitalize()+" :",value=str(char.pet[pet].lvl),inline=True)
            embd.add_field(name=lang["instinct"].capitalize()+" :",value=str(char.pet[pet].instinct),inline=True)
            embd.add_field(name=lang["force"].capitalize()+" :",value=str(char.pet[pet].force),inline=True)
            embd.add_field(name=lang["esprit"].capitalize()+" :",value=str(char.pet[pet].esprit),inline=True)
            embd.add_field(name=lang["charisme"].capitalize()+" :",value=str(char.pet[pet].charisme),inline=True)
            embd.add_field(name=lang["agilite"].capitalize()+" :",value=str(char.pet[pet].agilite),inline=True)
            embd.add_field(name=lang["karma"].capitalize()+" :",value=str(char.pet[pet].karma),inline=True)
            embd.add_field(name=lang["mod"].capitalize()+" :",value=modd,inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if command_check(prefix,message,'MJpetswitchmod',['mjpetswitchmod']):
            if get_args(prefix,message,'MJpetswitchmod',['mjpetswitchmod']).split(" ")[1] not in char.pet:
                yield from client.send_message(message.channel,lang["petnotfound"].format(get_args(prefix,message,'MJpetswitchmod',['mjpetswitchmod']).split(" ")[1]))
                return
            char = char.pet[get_args(prefix,message,'MJpetswitchmod',['mjpetswitchmod']).split(" ")[1]].switchmod()
            if char.pet[get_args(prefix,message,'MJpetswitchmod',['mjpetswitchmod']).split(" ")[1]].mod == 0: mod = lang["offensive"]
            else: mod = lang["defensive"]
            yield from client.send_message(message.channel,lang["switchmod"].format(get_args(prefix,message,'MJpetswitchmod',['mjpetswitchmod']).split(" ")[1],mod))
    if command_check(prefix,message,'setMJrole',['setmjrole']) and admin:
        srv.setmjrole(str(message.role_mentions[0].id))
        yield from client.send_message(message.channel,lang["setmjrole"].format(message.role_mentions[0].mention))
    if command_check(prefix,message,'JDRstart',['jdrstart','jdrcreate','JDRcreate']) and MJ:
        chan = message.channel_mentions[0]
        try:
            srv.getJDR(message.channel_mentions[0].id)
            yield from client.send_message(message.channel,lang["jdr_exist"].format(chan.mention))
        except:
            srv.jdrstart(str(chan.id),str(message.author.id))
            yield from client.send_message(message.channel,lang["jdr_start"].format(chan.mention,message.author.mention))
    if command_check(prefix,message,'JDRdelete',['jdrdelete']) and admin:
        chan = message.channel_mentions[0]
        curjdr = srv.getJDR(str(chan.id))
        yield from client.send_message(message.channel,lang["jdr_delete_confirm"].format(chan.mention))
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        curjdr.delete()
        charbase_exist = False
        yield from client.send_message(message.channel,lang["jdr_delete"].format(chan.mention))
    if command_check(prefix,message,'MJtransfer',['mjtransfer']) and chanMJ:
        if not MJrole in message.mentions[0].roles:
            yield from client.send_message(message.channel,lang["mjtransfer_notmj"])
            return
        yield from client.send_message(message.channel,lang["mjtransfer_step1"].format(message.channel.mention,message.mentions[0].mention))
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        yield from client.send_message(message.channel,lang["mjtransfer_step2"].format(message.mentions[0].mention,message.author.mention,message.channel.mention))
        confirm = yield from client.wait_for_message(timeout=60,author=message.mentions[0],channel=message.channel,content="accept")
        if confirm is None:
            yield from client.send_message(message.channel,lang["mjtransfer_timeout"].format(message.mentions[0].mention))
            return
        jdr.MJtransfer(str(message.mentions[0].id))
        yield from client.send_message(message.channel,lang["mjtransfer"].format(message.mentions[0].mention))
    if command_check(prefix,message,'JDRcopy',['jdrcopy']) and admin:
        if message.channel_mentions[0].server.id != message.server.id or message.channel_mentions[0].server.id != message.channel_mentions[1].server.id:
            yield from client.send_message(message.channel,lang["jdrcopy_serverror"])
            return
        yield from client.send_message(message.channel,lang["jdrcopy_confirm"].format(message.channel_mentions[0].mention,message.channel_mentions[1].mention))
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        src = message.channel_mentions[0]
        dest = message.channel_mentions[1]
        srv.getJDR(str(src.id)).copy(str(dest.id))
        yield from client.send_message(message.channel,lang["jdrcopy"])
    if command_check(prefix,message,'JDRextend',['jdrextend']) and admin:
        if message.channel_mentions[0].server.id != message.server.id or message.channel_mentions[0].server.id != message.channel_mentions[1].server.id:
            yield from client.send_message(message.channel,lang["jdrcopy_serverror"])
            return
        yield from client.send_message(message.channel,lang["jdrextend_confirm"].format(message.channel_mentions[0].mention,message.channel_mentions[1].mention))
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm")
        if confirm is None:
            yield from client.send_message(message.channel,lang["timeout"])
            return
        src = message.channel_mentions[0]
        dest = message.channel_mentions[1]
        try:
            destjdr = srv.getJDR(str(dest.id))
            destjdr.delete()
        except: pass
        srv.getJDR(str(src.id)).extend(str(dest.id))
        yield from client.send_message(message.channel,lang["jdrextend"])
    if command_check(prefix,message,'JDRunextend',['jdrunextend']) and (not command_check(prefix,message,'JDRunextend --all',['jdrunextend --all'])) and admin:
        if message.channel_mentions[0].server.id != message.server.id or message.channel_mentions[0].server.id != message.channel_mentions[1].server.id:
            yield from client.send_message(message.channel,lang["jdrcopy_serverror"])
            return
        src = message.channel_mentions[0]
        dest = message.channel_mentions[1]
        srv.getJDR(str(src.id)).unextend(str(dest.id))
        yield from client.send_message(message.channel,lang["jdrunextend"])
    if command_check(prefix,message,'JDRunextend --all',['jdrunextend --all']) and admin:
        src = message.channel_mentions[0]
        srv.getJDR(str(src.id)).unextend_all()
        yield from client.send_message(message.channel,lang["jdrunextend"])
    if command_check(prefix,message,'wiki'):
        query = message.content.replace(prefix+'wiki ',"")
        query = query.replace(" ","_")
        info = requests.get("http://thetaleofgreatcosmos.fr/wiki/api.php?action=parse&page="+query+"&format=json&redirects=true")
        exist_test = requests.get("http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query)
        if exist_test.status_code != 200:
            yield from client.send_message(message.channel,lang["wiki_unexisting"].format(str(exist_test.status_code)))
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
            embd.add_field(name=lang["wiki_redirect"],value=info.json()["parse"]["redirects"][0]["from"],inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'setfinalizer') and jdrchannel and chanMJ:
        msg = get_args(prefix,message,'setfinalizer')
        titl = msg.split("|")[0]
        while titl.endswith(" "): titl = titl[:-1]
        ct = msg.split("|")[1]
        while ct.startswith(" "): ct = ct[1:]
        jdr.set_finalizer_field(titl,ct)
        yield from client.send_message(message.channel,lang["finalizer_add"].format(titl,ct))
    if command_check(prefix,message,'delfinalizer',['deletefinalizer']) and jdrchannel and chanMJ:
        msg = get_args(prefix,message,'delfinalizer',['deletefinalizer'])
        jdr.del_finalizer_field(msg)
        yield from client.send_message(message.channel,lang["finalizer_del"].format(msg))
    if command_check(prefix,message,'finalize',['jdrfinalize','jdrend','JDRfinalize','JDRend']) and chanMJ:
        yield from client.send_message(message.channel,lang["finalize"])
        confirm = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content="confirm finalize")
        if confirm is None:
            yield from client.send_message(message.channel,lang["finalize_timeout"])
            return
        yield from client.send_message(message.channel,lang["finalize_start"])
        anoncer_isready = False
        if vocal:
            yield from vocal.append("Music/never_give_up_tsfh.mp3",False)#above_and_beyond_audiomachine.mp3",False)
            vocal.play()
        yield from asyncio.sleep(2)
        embd = discord.Embed(title="The Tale of Great Cosmos",colour=discord.Color(int("5B005B",16)))
        embd.set_image(url="https://cdn.discordapp.com/attachments/254997041858478080/317324181542928395/The_Tale_of_Great_Cosmos.png")
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_footer(text=time.asctime())
        yield from client.send_message(message.channel,embed=embd)
        yield from asyncio.sleep(5)
        msg = [("The Tale of Great Cosmos","Created by Ttgc\nAn original adventure in the world of Terae and the multiverse")]
        msg += [("Game Master (GM) :",str(discord.utils.get(message.server.members,id=jdr.mj)))]
        ct = ""
        for i in charbase:
            if i.linked is not None: ct += (str(discord.utils.get(message.server.members,id=i.linked))+" as "+i.name+"\n")
        msg += [("Players (PC) :",ct)]
        ct = ""
        for i in charbase:
            if i.dead: ct += (i.name+"\n")
        if ct == "": ct = "No player dead"
        msg += [("Deads Players during the adventure :",ct)]
        luck = []
        unluck = []
        rolled = []
        gstat = [0,0,0,0,0,0,0]
        for i in charbase:
            gstat = sum_ls(gstat,i.stat)
            rolled.append(i.stat[0])
            luck.append(100*((2*i.stat[1])+i.stat[2])/max(i.stat[0],1))
            unluck.append(100*((2*i.stat[-1])+i.stat[-2])/max(i.stat[0],1))
        ct = charbase[luck.index(max(luck))].name
        if charbase[luck.index(max(luck))].linked is not None: ct += (" ("+str(discord.utils.get(message.server.members,id=charbase[luck.index(max(luck))].linked))+")")
        msg += [("Most Lucky PC :",ct)]
        ct = charbase[unluck.index(max(unluck))].name
        if charbase[unluck.index(max(unluck))].linked is not None: ct += (" ("+str(discord.utils.get(message.server.members,id=charbase[unluck.index(max(unluck))].linked))+")")
        msg += [("Most Unlucky PC :",ct)]
        ct = charbase[rolled.index(max(rolled))].name
        if charbase[rolled.index(max(rolled))].linked is not None: ct += (" ("+str(discord.utils.get(message.server.members,id=charbase[rolled.index(max(rolled))].linked))+")")
        msg += [("Most dice rolled PC :",ct)]
        msg += [("Global statistics :",str(gstat[0])+" dices rolled\n"+str(gstat[1])+" super critic success\n"+str(gstat[-1])+" super critic fails\n"+str(gstat[2])+" critic success\n"+str(gstat[-2])+" critic fails\n"+str(gstat[3])+" success (without critic)\n"+str(gstat[-3])+" fails (without critic)")]
        for i in charbase:
            msg += [(i.name+" statistics :",str(i.stat[0])+" dices rolled\n"+str(i.stat[1])+" super critic success\n"+str(i.stat[-1])+" super critic fails\n"+str(i.stat[2])+" critic success\n"+str(i.stat[-2])+" critic fails\n"+str(i.stat[3])+" success (without critic)\n"+str(i.stat[-3])+" fails (without critic)")]
        msg += jdr.get_finalizer()
        msg += [("The Tale of Great Cosmos","Find more information on the official website/wiki\nJoin the community on the official discord")]
        msg += [("The Tale of Great Cosmos","Thank you for playing The Tale of Great Cosmos\nA chapter is closing, a new one is opening\nSee you soon in a new adventure")]
        for i in msg:
            titl = i[0]
            cont = i[1]
            embd = discord.Embed(title=titl,description=cont,colour=discord.Color(int("5B005B",16)))
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_footer(text=time.asctime())
            yield from client.send_message(message.channel,embed=embd)
            yield from asyncio.sleep(10)
        thanksmsg = yield from client.send_message(message.channel,"Thanks for playing **The Tale of Great Cosmos** !")
        yield from client.add_reaction(thanksmsg,"\U0001F4AF")
        yield from client.add_reaction(thanksmsg,"\U0001F51A")
        yield from client.add_reaction(thanksmsg,"\U0001F1EA")
        yield from client.add_reaction(thanksmsg,"\U0001F1F3")
        yield from client.add_reaction(thanksmsg,"\U0001F1E9")
        yield from client.send_message(message.channel,lang["finalize_end"])
        anoncer_isready = True
        jdr.delete()
    if command_check(prefix,message,'jdrlist',['JDRlist']) and admin:
        ls = srv.jdrlist()
        embd = discord.Embed(title=lang["jdrlist_title"],description=lang["jdrlist"],colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text=str(message.timestamp))
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for i in ls:
            info = lang["jdrlist_info"].format(discord.utils.get(message.server.members,id=i[3]).mention,str(i[2]),str(i[1]))
            embd.add_field(name="#{} :".format(str(discord.utils.get(message.server.channels,id=i[0]))),value=info,inline=True)
        yield from client.send_message(message.channel,embed=embd)

    #Other commands (not JDR)
    if command_check(prefix,message,'tell') and not command_check(prefix,message,'tell --tts',['tell -t']):
        msg = (message.content).replace(prefix+'tell ',"")
        print(str(message.author)+" (from : "+str(message.server)+") : "+msg)
        logf.append("/tell",str(message.author)+" (from : "+str(message.server)+") : "+msg)
        yield from client.delete_message(message)
        yield from client.send_message(message.channel,msg)
    if command_check(prefix,message,'tell --tts',['ttstell','telltts','tell -t']):
        msg = get_args(prefix,message,'tell --tts',['ttstell','telltts','tell -t'])
        print(str(message.author)+" (from : "+str(message.server)+") : "+msg)
        logf.append("/ttstell",str(message.author)+" (from : "+str(message.server)+") : "+msg)
        yield from client.delete_message(message)
        yield from client.send_message(message.channel,msg,tts=True)
    if command_check(prefix,message,'pi'):
        yield from client.send_message(message.channel,"3,141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 105 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 0679...\nhttp://www.nombrepi.com/")
    if command_check(prefix,message,'joke'):
        yield from client.send_message(message.channel,choice(["Pourquoi les japonais n'ont ils pas de chevaux ?\nParce qu'ils sont déjà poney (des japonais)",
                                                     "Pourquoi x^2 ressort-il de la foret en x ?\nParce qu'il s'est pris une racine !",
                                                     "Pourquoi 0 perd-il tous ses débats ?\nParce qu'il n'a pas d'argument !",
                                                     "Un proton dit a un electron : 'courage deprime pas ! Reste positif !",
                                                     "C'est une grenouille qui croyait qu'il était tôt mais en fait il était tard",
                                                     "Newton, Einstein et Pascal jouent à cache-cache\nEinstein commence à compter, Pascal part en courant se cacher \nNewton lui reste à coté d'Einstein et dessine un carré de 1 m de côté au sol et se place dedans\nEinstein se retourne et fait : 'Newton trouvé'\nCe à quoi Newton répond : 'non t'as trouvé 1 Newton sur 1 mètre carré, t'as trouvé 1 Pascal'",
                                                     "Heisenberg ,Schrodinger et Ohm sont dans une voiture quand ils sont stoppé par un agent de police. L’agent demande : « Savez-vous à quel vitesse vous roulez? » Heisenberg répond : « Non, mais je peux vous dire exactement où j’étais. »« Vous rouliez 20km/h au dessus de la limite ! »« Maintenant je suis perdu. »  L’agent pense qu’il y a lieu de faire une fouille et examine le coffre arrière et y découvre un chat mort. Il s’exclame : « Saviez-vous que vous avez un chat mort dans le coffre arrière. » Schrodinger répond : « Maintenant, je le sais! » L'agent décide de les arréter mais Ohm résiste.",
                                                     "Pourquoi les équations ont-elles le sens de l'humour?\nparce qu'elles ont du second degré!",
                                                     "Que dit-on d'une étudiante en lettres qui prépare son doctorat ?\nElle part en thèse (parenthèse)"]))
    if command_check(prefix,message,'nsfwjoke') and nsfw:
        yield from client.send_message(message.channel,choice(["Une mère tente d'ecouter au travers d'une porte ce que font ses 3 filles qui viennent de ramener chacune un petit ami pour la première fois.\nLa première rigole, la mère entre et voyant les deux au pieux demande pourquoi elle rigole, ce a quoi la première lui repond : 'une petite queue dans un grand trou ça chatouille !'\nLa seconde crie de douleur, la mère entre et demande pourquoi : 'Une grosse queue dans un petit trou ça fait mal'\nEnfin la mere n'entends rien venant de la troisième chambre, elle entre et vois sa fille en train de faire une pipe, et lui demande pourquoi on ne l'entends pas, ce a quoi lui répond sa fille : 'Voyons maman, il faut pas parler la bouche pleine !'",
                                                     "Le sexe c'est comme les équations, à partir de 3 inconnues ça devient intéressant",
                                                     "Un candidat passe l’oral de l’examen de sciences naturelles. L’examinateur plonge la main dans un sac, en sort un petit oiseau dont il montre la queue à l’étudiant:\n– Quel est le nom de cet oiseau ?\n– Heu.. je ne sais pas ! répond l'étudiant.\n– Je vais vous donner une autre chance.\nL’examinateur plonge à nouveau la main dans le sac et en sort un autre oiseau dont à nouveau il monte la queue:\n– Et celui-ci ? Quel est son nom ?\n– Je ne vois vraiment pas, monsieur !\n– Désolé, jeune homme ! Je regret, mais je me vois obliger de vous mettre un zéro ! Au fait, quel est votre nom ?\nLe candidat se lève, ouvre sa braguette et dit:\n– Devinez !",
                                                     "Et que dit-on de deux boules de pétanque qui entrent en collisions ?\nElles partent en couille",
                                                     "peut on appeller une maison vérouillée par son utilisateur lorsqu'il s'en va, une maison close ?",]))
    if command_check(prefix,message,'yay'):
        f = open("YAY.png","rb")
        yield from client.send_file(message.channel,f,content="YAY !")
        f.close()
    if command_check(prefix,message,'setgame') and botowner:
        statut = discord.Game(name=(message.content).replace(prefix+'setgame ',""))
        yield from client.change_presence(game=statut)
    if command_check(prefix,message,'choquedecu'):
        f=open("choquedecu.png","rb")
        yield from client.send_file(message.channel,f,content="#choquedecu")
        f.close()
    if command_check(prefix,message,'hentai') and nsfw:
        f = open("Hentai/"+choice(os.listdir("Hentai")),"rb")
        yield from client.send_file(message.channel,f)
        f.close()
    if command_check(prefix,message,'onichan'):
        f = open("onichan.jpg","rb")
        yield from client.send_file(message.channel,f)
        f.close()
    if command_check(prefix,message,'rule34') and nsfw:
        yield from client.send_message(message.channel,"Rule 34 : *If it exists, there is porn on it*\nhttps://rule34.paheal.net/")
    if command_check(prefix,message,'suggest'):
        pass
    if command_check(prefix,message,'shutdown') and botmanager:
        yield from client.send_message(message.channel,"You are requesting a shutdown, please ensure that you want to perform it by typing `confirm`")
        answer = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content='confirm')
        if answer is None:
            yield from client.send_message(message.channel,"Your request has timeout")
            return
        yield from vocalcore.interupt()
        yield from client.logout()
        sys.exit(0)
    if command_check(prefix,message,'reboot') and botmanager:
        yield from client.send_message(message.channel,"You are requesting a reboot, please ensure that you want to perform it by typing `confirm`")
        answer = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content='confirm')
        if answer is None:
            yield from client.send_message(message.channel,"Your request has timeout")
            return
        yield from vocalcore.interupt()
        yield from client.logout()
        sub.call(['./bootbot.sh'])
        sys.exit(0)
    if command_check(prefix,message,'blacklist') and botmanager:
        msg = message.content.replace(prefix+'blacklist ',"")
        ls = msg.split(" | ")
        blackid = ls[0]
        blacklist(blackid,ls[1])
        yield from client.send_message(message.channel,"The following id has been blacklisted : `"+str(blackid)+"` for \n```"+ls[1]+"```")
    if command_check(prefix,message,'unblacklist') and botmanager:
        blackid = message.content.replace(prefix+'unblacklist ',"")
        try:
            mb = DBMember(blackid)
        except: return
        mb.unblacklist()
        yield from client.send_message(message.channel,"The following id has been unblacklisted : `"+str(blackid)+"`")
    if command_check(prefix,message,'setbotmanager') and botowner:
        userid = message.content.replace(prefix+'setbotmanager ',"")
        grantuser(userid,'M')
        yield from client.send_message(message.channel,"The ID has been set as botmanager succesful")
    if command_check(prefix,message,'setpremium') and botowner:
        userid = message.content.replace(prefix+'setpremium ',"")
        grantuser(userid,'P')
        yield from client.send_message(message.channel,"The ID has been set as premium succesful")
    if command_check(prefix,message,'purgeserver',['purgeservers','purgesrv']) and botmanager:
        days = int(get_args(prefix,message,'purgeserver',['purgeservers','purgesrv']))
        purgeservers(days)
        yield from client.send_message(message.channel,"Purged servers successful")
    if command_check(prefix,message,'contentban') and admin:
        content = get_args(prefix,message,'contentban')
        if len(srv.wordblocklist()) < 20:
            if content.startswith(prefix):
                yield from client.send_message(message.channel,lang["contentban_prefix"])
            else:
                srv.blockword(content)
                yield from client.send_message(message.channel,lang["contentban"].format(content))
        else:
            yield from client.send_message(message.channel,lang["contentban_limit"])
    if command_check(prefix,message,'contentunban') and admin:
        content = message.content.replace(prefix+'contentunban ',"")
        srv.unblockword(content)
        yield from client.send_message(message.channel,lang["contentunban"].format(content))
    if command_check(prefix,message,'warn') and admin:
        if len(message.content.split("|")) < 2: return
        countstr = ""
        targetstr = ""
        for i in message.mentions:
            srv.warnuser(str(i.id))
            try: nbr = str(srv.get_warnnbr(DBMember(str(i.id))))
            except DatabaseException: nbr = "0"
            countstr += (str(i)+" : "+nbr+"\n")
            targetstr += (str(i)+", ")
        embd = discord.Embed(title="WARN",description=targetstr[:-2],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(message.timestamp))
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="https://www.ggte.unicamp.br/ea/img/iconalerta.png")
        embd.add_field(name="Reason :",value=message.content.split("|")[1],inline=True)
        embd.add_field(name="Total warnings :",value=countstr,inline=True)
        yield from client.send_message(message.channel,embed=embd)
        cfg = srv.get_warnconfig()
        for i in message.mentions:
            for k in cfg:
                if srv.get_warnnbr(DBMember(str(i.id))) >= k[0]:
                    try:
                        if k[1] == "kick":
                            yield from client.kick(i)
                            yield from client.send_message(message.channel,lang["warn_kick"].format(i.mention))
                            lgcodetarget = getuserlang(message.author.id)
                            if not lang_exist(lgcodetarget): lgcodetarget = "EN"
                            langtarget = get_lang(lgcodetarget)
                            yield from client.send_message(i,langtarget["warn_kick_user"].format(message.server.name))
                        elif k[1] == "ban":
                            yield from client.ban(i,0)
                            yield from client.send_message(message.channel,lang["warn_ban"].format(i.mention))
                            lgcodetarget = getuserlang(message.author.id)
                            if not lang_exist(lgcodetarget): lgcodetarget = "EN"
                            langtarget = get_lang(lgcodetarget)
                            yield from client.send_message(i,langtarget["warn_ban_user"].format(message.server.name))
                        else:
                            rl = None
                            for j in message.server.roles:
                                if str(j.id) == k[1]:
                                    rl = j
                                    break
                            if rl is not None:
                                yield from client.add_roles(i,rl)
                                yield from client.send_message(message.channel,lang["warn_assign"].format(i.mention,+rl.mention))
                    except discord.Forbidden: pass
                    break
    if command_check(prefix,message,'configwarn') and admin:
        msg = message.content.replace(prefix+'configwarn ',"")
        value = int(msg.split(" ")[0])
        sanction = msg.split(" ")[1].lower()
        if sanction == "assign":
            rl = message.role_mentions[0]
            srv.warnconfig(value,str(rl.id))
            yield from client.send_message(message.channel,lang["cfgwarn_assign"].format(rl.mention,str(value)))
        elif sanction == "kick":
            srv.warnconfig(value,"kick")
            yield from client.send_message(message.channel,lang["cfgwarn_kick"].format(str(value)))
        elif sanction == "ban":
            srv.warnconfig(value,"ban")
            yield from client.send_message(message.channel,lang["cfgwarn_ban"].format(str(value)))
        elif sanction == "remove":
            srv.warnconfig(value,"disable")
            yield from client.send_message(message.channel,lang["cfgwarn_none"].format(str(value)))
        else:
            yield from client.send_message(message.channel,lang["cfgwarn_unknown"])
    if command_check(prefix,message,'setadminrole',['adminrole']) and message.author == message.server.owner:
        srv.setadminrole(message.role_mentions[0].id)
        yield from client.send_message(message.channel,lang["setadmin"].format(message.role_mentions[0].mention))
    if command_check(prefix,message,'unwarn') and admin:
        countstr = ""
        targetstr = ""
        for i in message.mentions:
            srv.unwarnuser(str(i.id))
            try: nbr = str(srv.get_warnnbr(DBMember(str(i.id))))
            except DatabaseException: nbr = "0"
            countstr += (str(i)+" : "+nbr+"\n")
            targetstr += (str(i)+", ")
        embd = discord.Embed(title="UNWARN",description=targetstr[:-2],colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text=str(message.timestamp))
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        embd.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/interface-elements/32/accept-circle-512.png")
        embd.add_field(name="Total warnings :",value=countstr,inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'warnlist',['warnls']) and admin:
        ls = srv.get_warned()
        embd = discord.Embed(title="Warned list",description=lang["warnlist"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(message.timestamp))
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        for i in ls:
            user = yield from client.get_user_info(i[0])
            embd.add_field(name=str(user)+" :",value=str(i[1])+" warning(s)",inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'warnconfiglist',['warnconfigls','warncfgls','warncfglist']) and admin:
        ls = srv.get_warnconfig()
        embd = discord.Embed(title=lang["punishlist"],description=lang["warncfglist"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(message.timestamp))
        embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        for i in ls:
            if i[1] == "kick":
                sanction = "Kick"
            elif i[1] == "ban":
                sanction = "Ban"
            else:
                sanction = lang["warncfglist_assign"].format(discord.utils.get(message.server.roles,id=i[1]).mention)
            embd.add_field(name=str(i[0])+" warnings :",value=sanction,inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'setlang',['setlanguage']):
        lg = get_args(prefix,message,'setlang',['setlanguage']).upper()
        if lang_exist(lg):
            setuserlang(str(message.author.id),lg)
            yield from client.send_message(message.channel,get_lang(lg)["setlang"].format(lg))
    if command_check(prefix,message,'userblock') and admin:
        usr = get_args(prefix,message,'userblock')
        srv.blockusername(usr)
        yield from client.send_message(message.channel,lang["userblock"].format(usr))
    if command_check(prefix,message,'userunblock') and admin:
        usr = get_args(prefix,message,'userunblock')
        if not srv.unblockusername(usr):
            yield from client.send_message(message.channel,lang["userunblock_notexist"].format(usr))
        else:
            yield from client.send_message(message.channel,lang["userunblock"].format(usr))

    #KeepRole commands
    if command_check(prefix,message,'keeprole',['kr']) and admin:
        info = yield from client.application_info()
        if not message.server.get_member(info.id).server_permissions.manage_roles:
            yield from client.send_message(message.channel,lang["kr_notallowed"])
            return
        if command_check(prefix,message,'keeprole enabled',['kr enabled','kr switch','keeprole switch']):
            srv.togglekeeprole()
            srv = DBServer(srv.ID)
            if srv.keepingrole:
                yield from client.send_message(message.channel,lang["kr_on"])
            else:
                yield from client.send_message(message.channel,lang["kr_off"])
        if command_check(prefix,message,'keeprole roles add',['kr roles add','kr roles +','keeprole roles +']):
            strls = ""
            for i in message.role_mentions:
                if i.position < message.server.get_member(info.id).top_role.position:
                    strls += ("\n"+i.mention)
                    srv.addkeeprole(str(i.id))
            yield from client.send_message(message.channel,lang["kr_add"].format(strls))
        if command_check(prefix,message,'keeprole roles delete',['kr roles delete','kr roles -','keeprole roles -','kr roles del','keeprole roles del']):
            strls = ""
            for i in message.role_mentions:
                if i.position < message.server.get_member(info.id).top_role.position:
                    strls += ("\n"+i.mention)
                    srv.removekeeprole(str(i.id))
            yield from client.send_message(message.channel,lang["kr_del"].format(strls))
        if command_check(prefix,message,'keeprole clear',['kr clear']):
            srv.clearkeeprole()
            yield from client.send_message(message.channel,lang["kr_purge"])
        if command_check(prefix,message,'keeprole roles list',['kr roles list']):
            ls = srv.keeprolelist()
            rllist = ""
            for i in ls:
                rllist += (discord.utils.get(message.server.roles,id=i).mention+"\n")
            embd = discord.Embed(title="Keeprole system",description=lang["kr_roles"],colour=discord.Color(int('ff0000',16)))
            embd.set_footer(text=str(message.timestamp))
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.add_field(name="Roles list :",value=rllist,inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if command_check(prefix,message,'keeprole members list',['kr members list']):
            ls = srv.keeprolememberwithrole()
            mblist = {}
            for i in ls:
                if i[0] not in mblist:
                    mblist[i[0]] = []
                mblist[i[0]].append(i[1])
            embd = discord.Embed(title="Keeprole system",description=lang["kr_members"],colour=discord.Color(int('ff0000',16)))
            embd.set_footer(text=str(message.timestamp))
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            for i,k in mblist.items():
                rllist = ""
                for j in k:
                    rllist += (discord.utils.get(message.server.roles,id=j).mention+"\n")
                user = yield from client.get_user_info(i)
                embd.add_field(name=str(user)+" :",value=rllist,inline=True)
            yield from client.send_message(message.channel,embed=embd)

    #Vocal commands
    if command_check(prefix,message,'vocal on',['vocal off','music on','music off']) and premium:
        msg = get_args(prefix,message,'vocal',['music'])
        msg = msg.lower()
        if msg == "on" and not client.is_voice_connected(message.server):
            vocal = VocalSystem(str(message.server.id),vocalcore)
            yield from vocal.join(message.author.voice.voice_channel,message.channel)
            yield from client.send_message(vocal.textchan,lang["vocal_on"].format(str(message.author.voice.voice_channel),str(vocal.textchan)))
        elif msg == "off" and client.is_voice_connected(message.server) and (vocal is not None) and ((vocal.textchan == message.channel) or admin):
            chan = vocal.textchan
            yield from vocal.leave()
            vocalcore.removefromlist(str(message.server.id))
            yield from client.send_message(chan,lang["vocal_off"])
    if command_check(prefix,message,'ytplay',['play']) and (vocal is not None) and vocal.vocal and (vocal.textchan == message.channel) and premium:
        msg = get_args(prefix,message,'ytplay',['play'])
        yield from vocal.append(msg)
        vocal.play()
        yield from client.send_message(vocal.textchan,lang["ytplay"])
    if command_check(prefix,message,'musicskip',['skip']) and (vocal is not None) and vocal.vocal and (vocal.textchan == message.channel) and premium:
        vocal.skip()
        yield from client.send_message(vocal.textchan,lang["musicskip"])
    if command_check(prefix,message,'playlocal') and botmanager and (vocal is not None) and vocal.vocal and (vocal.textchan == message.channel):
        msg = (message.content).replace(prefix+'playlocal ',"")
        if not msg in os.listdir("Music/"):
            if msg+".mp3" in os.listdir("Music/"): msg += ".mp3"
            elif msg+".wav" in os.listdir("Music/"): msg += ".wav"
            else:
                yield from client.send_message(message.channel,lang["playlocal_notfound"])
                return
        yield from vocal.append("Music/"+msg,False)
        vocal.play()
        yield from client.send_message(vocal.textchan,lang["playlocal"])
    if command_check(prefix,message,'disconnectvocal') and botmanager:
        yield from client.send_message(message.channel,"This will disconnect the bot from all vocal connections, are you sure ?\nType `confirm` to do it")
        answer = yield from client.wait_for_message(timeout=60,author=message.author,channel=message.channel,content='confirm')
        if answer is None:
            yield from client.send_message(message.channel,"Your request has timeout")
            return
        yield from vocalcore.interupt()
    if command_check(prefix,message,'apart') and chanMJ and message.author.voice.voice_channel is not None:
        linked = []
        for i in charbase:
            if i.linked is not None: linked.append(i.linked)
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
    if command_check(prefix,message,'debug',['eval']) and botowner:
        msg = get_args(prefix,message,'debug',['eval'])
        print("running debug instruction : "+msg)
        logf.append("/debug","running debug instruction : "+msg)
        exec(msg)
    if command_check(prefix,message,'help','?'):
        yield from client.send_message(message.channel,"Check all avalaible command here : https://ttgc.github.io/TtgcBot/")
##        f = open("help.txt","r")
##        msg = f.read()
##        ls = msg.split("\n\n")
##        if message.content.startswith(prefix+'help normal'):
##            yield from client.send_message(message.author,"Here's the whole list of normal commands :\n"+ls[0])
##        elif message.content.startswith(prefix+'help vocal'):
##            yield from client.send_message(message.author,"Here's the whole list of vocal commands :\n"+ls[1])
##        elif message.content.startswith(prefix+'help JDR'):
##            yield from client.send_message(message.author,"Here's the whole list of JDR commands :\n"+ls[2])
##            yield from client.send_message(message.author,ls[3])
##        else:
##            yield from client.send_message(message.author,"Here's the whole list of my commands (somes will need some rights) :\n")
##            for i in ls:
##                yield from client.send_message(message.author,i)
##        f.close()
##        yield from client.send_message(message.channel,"I've sent you a private message with the answer")
    if command_check(prefix,message,'invite',['invit']):
        botaskperm = discord.Permissions().all()
        botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_server = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
        url = discord.utils.oauth_url(str(client.user.id),botaskperm)
        embd = discord.Embed(title="TtgcBot",description=lang["invite"],colour=discord.Color(randint(0,int('ffffff',16))),url=url)
        embd.set_footer(text=lang["invite_author"],icon_url=client.user.avatar_url)
        embd.set_image(url=client.user.avatar_url)
        embd.set_author(name="Ttgc",icon_url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/08/avatar-2-perso.png",url=url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["invite_srv"],value=str(len(client.servers))+" servers",inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if command_check(prefix,message,'jointhegame',['jointtgc','joinTTGC','ttgc','TTGC']):
        inv = yield from client.create_invite(client.get_server("326648561976737792"),max_age=3600)
        yield from client.send_message(message.channel,"Rejoignez le serveur officiel The Tale of Great Cosmos (serveur FR) : \n"+str(inv.url))
    if command_check(prefix,message,'ping'):
        tps_start = time.clock()
        yield from client.send_message(message.channel,":ping_pong: pong ! :ping_pong:")
        tps_end = time.clock()
        ping = round((tps_end-tps_start)*1000)
        yield from client.send_message(message.channel,lang["ping"].format(str(ping)))
    logf.stop()
    yield from client.change_presence(game=statut)

@client.event
@asyncio.coroutine
def on_member_join(member):
    srv = DBServer(str(member.server.id))
    userblocked = srv.blockuserlist()
    for i in userblocked:
        if i in str(member).split("#")[0]:
            yield from asyncio.sleep(1)
            yield from client.ban(member,1)
            return
    if srv.keepingrole:
        yield from asyncio.sleep(1)
        yield from srv.restorerolemember(client,member.server,member)

@client.event
@asyncio.coroutine
def on_member_remove(member):
    srv = DBServer(str(member.server.id))
    if srv.keepingrole:
        srv.backuprolemember(member)

@client.event
@asyncio.coroutine
def on_server_join(server):
    addserver(server)

@client.event
@asyncio.coroutine
def on_server_remove(server):
    srv = DBServer(server.id)
    srv.remove()

@client.event
@asyncio.coroutine
def on_error(event,*args,**kwargs):
    message = args[0]
    lgcode = getuserlang(message.author.id)
    if not lang_exist(lgcode): lgcode = "EN"
    lang = get_lang(lgcode)
    logging.warning(traceback.format_exc())
    yield from client.send_message(message.channel,lang["error"].format(traceback.format_exc(limit=1000)))

@client.event
@asyncio.coroutine
def on_ready():
    global logf
    yield from client.change_presence(game=statut)
    logf.restart()
    botaskperm = discord.Permissions().all()
    botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_server = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
    url = discord.utils.oauth_url(str(client.user.id),botaskperm)
    print(url)
    logf.append("Initializing","Generating invite link : "+str(url))
    srvid = []
    for i in client.servers:
        srvid.append(str(i.id))
        if str(i.id) not in srvlist():
            addserver(i)
            try: logf.append("Initializing","This server has invited the bot during off period, adding it to the database : "+str(i)+" (ID="+str(i.id)+")")
            except: logf.append("Initializing","Server added (ID="+str(i.id)+")")
    logf.append("Initializing","Added new servers to the database successful")
    purgeservers(365)
    logf.append("Initializing","Purge servers who has kicked the bot at least one year ago successful")
    for i in srvlist():
        if i not in srvid:
            srv = DBServer(i)
            logf.append("Initializing","This server has kicked the bot during off period, removing it from the database : ID="+str(i))
            srv.remove()
    logf.append("Initializing","Removed old servers from the database successful")
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
