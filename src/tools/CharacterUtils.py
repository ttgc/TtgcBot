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

from src.utils.DatabaseManager import *
#from tools.BotTools import DBJDR

class Item:
    def __init__(self,name,weight):
        self.name = name
        self.weight = weight

    def __str__(self):
        return self.name+" ("+self.weight+")"

class Inventory:
    def __init__(self,maxw=20):
        self.items = {}
        self.maxweight = 20
        self.weight = 0
        self.character = None
        self.jdr = None
        self.ID = None

    def __str__(self):
        itemstring = []
        for i,k in self.items.items():
            itemstring.append("{}{}".format(i.name, " x{}".format(str(k)) if k > 1 else ""))
        return ", ".join(itemstring)

    def bind(self,char,jdr):
        self.character = char
        self.jdr = jdr

    def loadfromdb(self,inventory_id):
        db = Database()
        cur = db.execute("SELECT item_name,qte,weight FROM items WHERE id_inventory = %(idinv)s;",idinv=inventory_id)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the inventory")
        self.items = {}
        for i in cur:
            it = Item(i[0],i[2])
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
        db.call("additem",dbkey=self.character.key,idserv=self.jdr.server,idchan=self.jdr.channel,itname=it.name,quantite=qte,poids=it.weight)
        db.close()
        self.loadfromdb(self.ID)

    def rmitem(self,it,qte):
        db = Database()
        db.call("removeitem",dbkey=self.character.key,idserv=self.jdr.server,idchan=self.jdr.channel,itname=it.name,quantite=qte)
        db.close()
        self.loadfromdb(self.ID)

    @staticmethod
    def forceinvcalc():
        db = Database()
        db.call("forceinvcalc")
        db.close()

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
        self.extension = Extension(row[5])

    def skillsearch(skname):
        db = Database()
        rows = db.call("skillsearch",name=skname)
        if rows is None:
            db.close(True)
            return []
        ls = []
        for i in rows:
            ls.append(Skill(i[0]))
        db.close()
        return ls
    skillsearch = staticmethod(skillsearch)

    def isskillin(ls,skid):
        for i in ls:
            if i.ID == skid: return True
        return False
    isskillin = staticmethod(isskillin)

class Extension:
    def __init__(self,ID):
        self.ID = ID
        db = Database()
        rows = db.execute("SELECT universe, world FROM Extensions WHERE id_extension = %(ext)s",ext=self.ID)
        if rows is None:
            db.close(True)
            raise DatabaseException("Extension ID not found")
        row = rows.fetchone()
        db.close()
        self.universe = row[0]
        self.world = row[1]

    def __str__(self):
        return "{} : {}".format(self.universe, self.world)

def retrieveCharacterOrigins(cl):
    db = Database()
    cur = db.execute("SELECT classe.nom,race.nom FROM classe INNER JOIN race ON classe.id_race = race.id_race WHERE id_classe = %(ID)s",ID=cl)
    if cur is None:
        db.close(True)
        raise DatabaseException("Class ID not found")
    row = cur.fetchone()
    db.close()
    return row[1],row[0]

def retrieveClassID(rcid,clname):
    db = Database()
    cur = db.execute("SELECT id_classe FROM classe WHERE lower(nom) = %(name)s AND id_race = %(rc)s",name=clname.lower(),rc=rcid)
    if cur is None:
        db.close(True)
        raise DatabaseException("Class Name not found")
    row = cur.fetchone()
    db.close()
    return row

def retrieveRaceID(rcname):
    db = Database()
    cur = db.execute("SELECT id_race FROM race WHERE lower(nom) = %(name)s",name=rcname.lower())
    if cur is None:
        db.close(True)
        raise DatabaseException("Race Name not found")
    row = cur.fetchone()
    db.close()
    return row

def retrieveRaceName(rcid):
    if rcid is None: return None
    db = Database()
    cur = db.execute("SELECT nom FROM race WHERE id_race = %(rc)s",rc=rcid)
    if cur is None:
        db.close(True)
        raise DatabaseException("Race Name not found")
    row = cur.fetchone()
    db.close()
    return row

def retrieveSymbiontID(sbname):
    db = Database()
    cur = db.execute("SELECT id_symbiont FROM symbiont WHERE lower(nom) = %(name)s",name=sbname.lower())
    if cur is None:
        db.close(True)
        raise DatabaseException("Symbiont Name not found")
    row = cur.fetchone()
    db.close()
    return row

def retrieveSymbiontName(sbid):
    if sbid is None: return None
    db = Database()
    cur = db.execute("SELECT nom FROM symbiont WHERE id_symbiont = %(sb)s",sb=sbid)
    if cur is None:
        db.close(True)
        raise DatabaseException("Race Name not found")
    row = cur.fetchone()
    db.close()
    return row

def retrieveOrganization(orgid):
    db = Database()
    cur = db.execute("SELECT nom FROM organizations WHERE id_org = %(id)s",id=orgid)
    if cur is None:
        db.close()
        return None
    row = cur.fetchone()
    db.close()
    return row[0] if row is not None else None

def isOrganizationHidden(orgname):
    db = Database()
    cur = db.execute("SELECT hidden FROM organization WHERE nom = %(org)s", org=orgname)
    if cur is None:
        db.close()
        return False
    row = cur.fetchone()
    db.close()
    return row[0] if row is not None else False

def organizationExists(orgname):
    db = Database()
    cur = db.execute("SELECT COUNT(*) FROM organizations WHERE nom = %(org)s",org=orgname)
    if cur is None:
        db.close(True)
        raise DatabaseException("Error when fetching organization table")
    nbr = cur.fetchone()[0]
    db.close()
    return nbr > 0

def retrieveOrganizationSkill(orgname):
    db = Database()
    cur = db.call("get_orgskills",org=orgname)
    if cur is None:
        db.close()
        return []
    ls = []
    for i in row:
        ls.append(Skill(i[0]))
    db.close()
    return ls

def retrieveRaceSkill(racename):
    db = Database()
    cur = db.call("get_raceskills",racename=racename)
    if cur is None:
        db.close()
        return []
    ls = []
    for i in row:
        ls.append(Skill(i[0]))
    db.close()
    return ls
