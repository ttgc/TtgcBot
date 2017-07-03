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
import logging
import time
from EventManager import *
import os
import zipfile

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

global prefix
global charbase
charbase = {}
global linked
linked = {}
global char
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
    def __init__(self,dic={"name":"","lore":"","PV":1,"PM":1,"force":50,"esprit":50,"charisme":50,"furtivite":50,"karma":0,"money":0,"stat":[0,0,0,0,0,0,0],"lp":0,"dp":0,"regenkarm":0.1,"mod":0,"armor":0,"RM":0}):
        self.name = dic["name"]
        self.lore = dic["lore"]
        self.PVmax = self.PV = dic["PV"]
        self.PMmax = self.PM = dic["PM"]
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
        return self.name+"\n"+self.lore

    def check_life(self):
        if self.PV <= 0:
            return False
        else:
            return True

    def stock(self):
        return "<"+self.name+"|"+self.lore+"|"+str(self.PVmax)+"|"+str(self.PMmax)+"|"+str(self.force)+"|"+str(self.esprit)+"|"+str(self.charisme)+"|"+str(self.furtivite)+"|"+str(self.money)+"|"+str(self.lp)+"|"+str(self.dp)+"|"+str(self.regenkarm[1])+"|"+str(self.mod)+"|"+str(self.armor)+"|"+str(self.RM)+">"

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
    global charbase
    string = string.replace("<","")
    string = string.replace(">","")
    ls = string.split("|")
    st = convert_str_into_ls(ls[-1])
    charbase[name] = Character({"name":ls[0],"lore":ls[1],"PV":int(ls[2]),"PM":int(ls[3]),"force":int(ls[4]),"esprit":int(ls[5]),"charisme":int(ls[6]),"furtivite":int(ls[7]),"karma":0,"money":int(ls[8]),"stat":[0,0,0,0,0,0,0],"lp":int(ls[9]),"dp":int(ls[10]),"regenkarm":float(ls[11]),"mod":int(ls[12]),"armor":int(ls[13]),"RM":int(ls[14])})

def convert_str_into_dic(string):
    if string == "{}": return {}
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
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

def save_data():
    pass

client = discord.Client()

@client.event
@asyncio.coroutine
def on_message(message):
    global prefix,charbase,char,file,linked,sex,logf,ideas,statut,events,vocal,vocalco,song,mobs,anoncer_isready
    logf.restart()
    #special values
    jdrchannel = False
    admin = False
    botowner = False
    nsfw = False
    musicchannel = False
    if str(message.author.id) == "222026592896024576":
        botowner = admin = True
    if str(message.author) in linked:
        char = charbase[linked[str(message.author)]]
    if message.server != None:
        if message.author == message.server.owner: admin = True
    if message.channel.id == "238929721449119745": jdrchannel = True
    if message.channel.name.startswith("nsfw-"): nsfw = True
    if message.channel.id == "237668457963847681": musicchannel = True
    #commands
    #########REWRITTEN##########
    #####NOT YET REWRITTEN######
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

    if message.content.startswith(prefix+'nsfwjoke'):
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
    if message.content.startswith(prefix+'rule34') and nsfw:
        yield from client.send_message(message.channel,"Rule 34 : *If it exists, there is porn on it*\nhttps://rule34.paheal.net/")
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
##    save_data()
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
def on_ready():
    global logf
    yield from client.change_presence(game=statut)
    logf.restart()
    logf.append("Initializing","Bot is now ready")
    logf.stop()

@asyncio.coroutine
def main_task():
    yield from client.login('')
    yield from client.connect()

def launch():
    global file,prefix,charbase,linked,logf,ideas,events
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

