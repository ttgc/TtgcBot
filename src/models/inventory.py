#!usr/bin/env python3
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

from datahandler.database import Database
from datahandler.api import APIManager
from utils.decorators import deprecated
from exceptions import APIException, DatabaseException
from network import RequestType

class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __str__(self):
        return f"{self.name} ({self.weight})"


class Inventory:
    def __init__(self, maxw=20):
        self.items = {}
        self.maxweight = 20
        self.weight = 0
        self.character = None
        self.jdr = None
        self.ID = None

    def __getitem__(self, it):
        return self.items.get(self.items[it], None)

    def __setitem__(self, it, value):
        self.items[it] = value

    def __str__(self):
        itemstring = []
        for i, k in self.items.items():
            itemstring.append("{}{}".format(i.name, " x{}".format(str(k)) if k > 1 else ""))
        return ", ".join(itemstring)

    def bind(self, char, jdr):
        self.character = char
        self.jdr = jdr

    @classmethod
    async def char_loadfromdb(cl, srv, channel, charkey, requester, requesterRole, maxsize):
        api = APIManager()
        info = await api(RequestType.GET, "Inventory/{}/{}/{}".format(srv, channel, charkey),
            resource="SRV://{}/{}/{}".format(srv, channel, charkey), requesterID=requester, roleID=requesterRole)

        if info.status // 100 != 2:
            raise APIException("Character inventory get error", srv=srv, channel=channel, charkey=charkey, code=info.status)

        inv = cl(maxsize)
        for i in info.result:
            it = Item(i.get("info", {}).get("name", ""), i.get("info", {}).get("weight", 1))
            inv[it] = i.get("quantity", 1)
        return inv

    @classmethod
    async def pet_loadfromdb(cl, srv, channel, charkey, petkey, requester, requesterRole, maxsize):
        api = APIManager()
        info = await api(RequestType.GET, "Inventory/{}/{}/{}/{}".format(srv, channel, charkey, petkey),
            resource="SRV://{}/{}/{}/{}".format(srv, channel, charkey, petkey), requesterID=requester, roleID=requesterRole)

        if info.status // 100 != 2:
            raise APIException("Pet inventory get error", srv=srv, channel=channel, charkey=charkey, petkey=petkey, code=info.status)

        inv = cl(maxsize)
        for i in info.result:
            it = Item(i.get("info", {}).get("name", ""), i.get("info", {}).get("weight", 1))
            inv[it] = i.get("quantity", 1)
        return inv

    @deprecated("Old feature using DatabaseManager")
    def _reload(self):
        db = Database()
        cur = db.execute("SELECT size_,size_max FROM inventaire WHERE id_inventory = %(idinv)s;", idinv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to reload the inventory")
        info = cur.fetchone()
        db.close()
        self.weight = info[0]
        self.maxweight = info[1]

    def __add__(self, it):
        return self.additem(it, 1)

    def __iadd__(self, it):
        return self.additem(it, 1)

    def __sub__(self, it):
        return self.rmitem(it, 1)

    def __isub__(self, it):
        return self.rmitem(it, 1)

    @deprecated("Old feature using DatabaseManager")
    def additem(self, it, qte):
        db = Database()
        db.call("additem", dbkey=self.character.key, idserv=self.jdr.server, idchan=self.jdr.channel, itname=it.name, quantite=qte, poids=it.weight)
        db.close()
        self.loadfromdb(self.ID)

    @deprecated("Old feature using DatabaseManager")
    def rmitem(self, it, qte):
        db = Database()
        db.call("removeitem", dbkey=self.character.key, idserv=self.jdr.server, idchan=self.jdr.channel, itname=it.name, quantite=qte)
        db.close()
        self.loadfromdb(self.ID)

    @deprecated("Old feature using DatabaseManager")
    @staticmethod
    def forceinvcalc():
        db = Database()
        db.call("forceinvcalc")
        db.close()
