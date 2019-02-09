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

class Skill:
    def __init__(self,ID):
        self.ID = ID
        db = Database()
        rows = db.call("skillinfo",idskill=ID)
        if rows is None:
            db.close(True)
            raise DatabaseException("Skill ID not found")
        row = rows.fetchone()
        db.close()
        self.name = row[1]
        self.description = row[2]
        self.origine = row[3]

    def skillsearch(skname):
        db = Database()
        rows = db.call("skillsearch",name=skname)
        if rows is None:
            db.close(True)
            return []
        db.close()
        ls = []
        for i in rows:
            ls.append(Skill(i[0]))
        return ls
    skillsearch = staticmethod(skillsearch)

def retrieveCharacterOrigins(cl):
    db = Database()
    cur = db.execute("SELECT classe.nom,race.nom FROM classe INNER JOIN classe.id_race = race.id_race WHERE id_classe = %(ID)d",ID=cl)
    if cur is None:
        db.close(True)
        raise DatabaseException("Class ID not found")
    row = cur.fetchone()
    db.close()
    return row[1],row[0]

def retrieveClassID(clname):
    db = Database()
    cur = db.execute("SELECT id_classe FROM classe WHERE nom = %(name)s",name=clname)
    if cur is None:
        db.close(True)
        raise DatabaseException("Class Name not found")
    row = cur.fetchone()
    db.close()
    return row
