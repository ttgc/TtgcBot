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
from BotTools import DBJDR

class Item:
    def __init__(self,name,descr,weight):
        self.name = name
        self.description = descr
        self.weight = weight
        self.ID = None

    def __str__(self):
        return self.name+" ("+self.weight+") : "+self.description

    def create(self):
        db = Database()
        cur = db.call("createitem",name=self.name,descr=self.description,poids=self.weight)
        if cur is None:
            db.close(True)
            raise DatabaseError("unable to create the item")
        self.ID = cur.fetchone()[0]
        db.close()

    def load(self):
        db = Database()
        cur = db.execute("SELECT id_item FROM Items WHERE nom = %(nom)s AND description = %(descr)s AND weight = %(poids)s;",nom=self.name,descr=self.description,poids=self.weight)
        if cur is None:
            db.close(True)
            raise DatabaseErrror("unable to load the item")
        self.ID = cur.fetchone()[0]
        db.close()

    def delete(self):
        if self.ID is None:
            raise AttributeError("self.ID is not defined for this item, maybe it has not be loaded or created before")
        db = Database()
        db.call("deleteitem",item=self.ID)
        db.close()

    def find(name):
        db = Database()
        cur = db.execute("SELECT id_item,description,weight FROM Items WHERE nom = %(nom)s;",nom=name)
        if cur is None:
            db.close(True)
            raise DatabaseError("unable to find the item")
        it = cur.fetchone()
        if it is None:
            db.close(True)
            return None
        db.close()
        item = Item(name,it[1],it[2])
        item.ID = it[0]
        return item
    find = staticmethod(find)

class Inventory:
    def __init__(self,maxw=20):
        self.items = {}
        self.maxweight = 20
        self.weight = 0
        self.character = None
        self.jdr = None
        self.ID = None

    def bind(self,char,jdr):
        self.character = char
        self.jdr = jdr

    def loadfromdb(self,inventory_id):
        db = Database()
        cur = db.execute("SELECT nom,qte,description,weight FROM contient INNER JOIN items ON (contient.id_item = items.id_item) WHERE id_inventory = %(idinv)s;",idinv=inventory_id)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the inventory")
        self.items = {}
        for i in cur:
            it = Item(i[0],i[2],i[3])
            it.load()
            self.items[it] = i[1]
        db.close()
        self.ID = inventory_id
        self._reload()

    def _reload(self):
        db = Database()
        cur = db.execute("SELECT size_,size_max FROM inventaire WHERE id_inventory = %(idinv)s;",idinv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseErrror("unable to reload the inventory")
        info = cur.fetchone()
        db.close()
        self.weight = info[0]
        self.maxweight = info[1]

    def __add__(self,it):
        return self.additem(it,1)

    def __iadd__(self,it):
        return self.additem(it,1)

    def __sub__(self,it):
        return self.rmitem(it,1)

    def __isub__(self,it):
        return self.rmitem(it,1)

    def additem(self,it,qte):
        db = Database()
        db.call("additem",dbkey=self.character.key,idserv=self.jdr.server,idchan=self.jdr.channel,itname=it.name,quantite=qte)
        db.close()
        self.loadfromdb(self.ID)
        
    def rmitem(self,it,qte):
        db = Database()
        db.call("removeitem",dbkey=self.character.key,idserv=self.jdr.server,idchan=self.jdr.channel,itname=it.name,quantite=qte)
        db.close()
        self.loadfromdb(self.ID)

class Character:
    """Character class"""
    def __init__(self,dic={"charkey":"","name":"","lore":"","PVm":1,"PMm":1,"force":50,"esprit":50,"charisme":50,"furtivite":50,"karma":0,"money":0,"stat":[0,0,0,0,0,0,0],"lp":0,"dp":0,"regenkarm":0.1,"mod":0,"armor":0,"RM":0,"PV":1,"PM":1,"default_mod":0,"default_karma":0,"intuition":3,"mentalhealth":100,"lvl":1,"linked":None,"inventory":Inventory()}):
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
        self.jdr = None
        #mod 0 = offensiv / mod 1 = defensiv

    def __str__(self):
        return self.name

    def bind(self,jdr):
        self.inventory.bind(self,jdr)
        self.jdr = jdr

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
    def roll(self,client,channel,stat,modifier):
        if stat == "force":
            self.stat[0] += 1
            dice = randint(1,100)
            kar = randint(1,10)
            result = dice
            if result == 42:
                self.stat[1] += 1
                yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                self.charset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                self.charset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.force+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (force) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(self.force+modifier))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.force+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (force) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(self.force+modifier))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.charset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.charset('kar',-1)
                        self.karma -= 1
                    elif result <= self.force+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (force) :"+str(result)+"/"+str(self.force+modifier))
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
                yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                self.charset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                self.charset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.esprit+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (esprit) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(self.esprit+modifier))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.esprit+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (esprit) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(self.esprit+modifier))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.charset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.charset('kar',-1)
                        self.karma -= 1
                    elif result <= self.esprit+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (esprit) :"+str(result)+"/"+str(self.esprit+modifier))
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
                yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                self.charset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                self.charset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.charisme+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (charisme) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(self.charisme+modifier))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.charisme+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (charisme) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(self.charisme+modifier))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.charset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.charset('kar',-1)
                        self.karma -= 1
                    elif result <= self.charisme+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (charisme) :"+str(result)+"/"+str(self.charisme+modifier))
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
                yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                self.charset('kar',-2)
                self.karma -= 2
            elif result == 66:
                self.stat[-1] += 1
                yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                self.charset('kar',2)
                self.karma += 2
            else:
                if self.karma >= 5:
                    result -= kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.furtivite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (agilite) :"+str(result)+" ("+str(dice)+"-"+str(kar)+") /"+str(self.furtivite+modifier))
                elif self.karma <= -5:
                    result += kar
                    if result == 42:
                        self.stat[1] += 1
                        yield from client.send_message(channel,"God damn it ! You scored a 42 !!!",tts=True)
                        self.charset('kar',-2)
                        self.karma -= 2
                    elif result == 66:
                        self.stat[-1] += 1
                        yield from client.send_message(channel,"Oh Shit ! That's also called a 66",tts=True)
                        self.charset('kar',2)
                        self.karma += 2
                    else:
                        if result >= 91:
                            self.stat[-2] += 1
                            self.charset('kar',1)
                            self.karma += 1
                        elif result <= 10:
                            self.stat[2] += 1
                            self.charset('kar',-1)
                            self.karma -= 1
                        elif result <= self.furtivite+modifier: self.stat[3] += 1
                        else: self.stat[-3] += 1
                        yield from client.send_message(channel,"Result of test (agilite) :"+str(result)+" ("+str(dice)+"+"+str(kar)+") /"+str(self.furtivite+modifier))
                else:
                    if result == 42: self.stat[1] += 1
                    elif result == 66: self.stat[-1] += 1
                    elif result >= 91:
                        self.stat[-2] += 1
                        self.charset('kar',1)
                        self.karma += 1
                    elif result <= 10:
                        self.stat[2] += 1
                        self.charset('kar',-1)
                        self.karma -= 1
                    elif result <= self.furtivite+modifier: self.stat[3] += 1
                    else: self.stat[-3] += 1
                    yield from client.send_message(channel,"Result of test (agilite) :"+str(result)+"/"+str(self.furtivite+modifier))
    ##            if self.regenkarm[0] >= 1:
    ##                if self.karma < 0: self.karma += 1
    ##                elif self.karma > 0: self.karma -= 1
    ##                self.regenkarm[0] -= 1
            db = Database()
            db.call("hasroll",dbkey=self.key,idserv=self.jdr.server,idchan=self.jdr.channel,valmax=self.furtivite+modifier,val=result)
            db.close()
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
                self.charset('kar',1)
                self.karma += 1
                if self.karma > 10: self.karma = 10
            else:
                self.charset('kar',-1)
                self.karma -= 1
                if self.karma < -10: self.karma = -10
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
            yield from client.send_message(channel,"Result of test (intuition) :"+str(result)+"/"+str(self.intuition+modifier))
        if self.karma > 10: self.karma = 10
        if self.karma < -10: self.karma = -10
