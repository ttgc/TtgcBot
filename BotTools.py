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
from DatabaseManager import *
from Character import *

class DBServer:
    def __init__(self,ID):
        self.ID = ID
        db = Database()
        cur = db.execute("SELECT * FROM Serveur WHERE id_server = %(idserv)s;",idserv=ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the server")
        info = cur.fetchone()
        db.close()
        self.mjrole = info[1]
        self.prefix = info[2]
        self.keepingrole = info[3]
        self.adminrole = info[4]

    def togglekeeprole(self):
        self.keepingrole = not self.keepingrole
        db = Database()
        db.call("togglekeepingrole",idserv=self.ID)
        db.close()

    def setmjrole(self,roleid):
        self.mjrole = roleid
        db = Database()
        db.call("setroleserver",idserv=self.ID,rltype="M",rol=roleid)
        db.close()

    def setadminrole(self,roleid):
        self.mjrole = roleid
        db = Database()
        db.call("setroleserver",idserv=self.ID,rltype="A",rol=roleid)
        db.close()

    def setprefix(self,prefix):
        self.prefix = prefix
        db = Database()
        db.call("setprefix",idserv=self.ID,pref=prefix)
        db.close()

    def keeprolelist(self):
        db = Database()
        cur = db.execute("SELECT id_role FROM Keeprole WHERE id_server = %(idserv)s GROUP BY id_role;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the keeprole list")
        ls = []
        for i in cur:
            ls.append(i[0])
        db.close()
        return ls

    def keeprolemember(self):
        db = Database()
        cur = db.execute("SELECT id_member FROM Keeprole WHERE id_server = %(idserv)s GROUP BY id_member;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the keeprole member list")
        ls = []
        for i in cur:
            ls.append(i[0])
        db.close()
        return ls

    def keeprolememberwithrole(self):
        db = Database()
        cur = db.execute("SELECT id_member,id_role FROM Keeprole WHERE id_server = %(idserv)s;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the keeprole member/roles list")
        ls = cur.fetchall()
        db.close()
        return ls

    def wordblocklist(self):
        db = Database()
        cur = db.execute("SELECT content FROM Word_Blocklist WHERE id_server = %(idserv)s;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the blocked word list")
        ls = []
        for i in cur:
            ls.append(i[0])
        db.close()
        return ls

    def jdrlist(self):
        db = Database()
        cur = db.execute("SELECT id_channel,creation,PJs,id_member FROM JDR WHERE id_server = %(idserv)s;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the jdr list")
        ls = cur.fetchall()
        db.close()
        db = Database()
        cur = db.execute("SELECT id_target FROM JDRextension WHERE id_server = %(idserv)s;",idserv=self.ID)
        if cur is not None:
            extended = []
            for i in cur:
                extended.append(i[0])
            for i in ls:
                if i[1] in extended:
                    ls.remove(i)
        db.close()
        return ls

    def blockword(self,string):
        db = Database()
        db.call("blockword",idserv=self.ID,word=string)
        db.close()

    def unblockword(self,string):
        db = Database()
        db.call("unblockword",idserv=self.ID,word=string)
        db.close()

    def backuprolemember(self,member):
        db = Database()
        ls = self.keeprolelist()
        for i in member.roles:
            if str(i.id) in ls:
                db.call("backuprolemember",idmemb=member.id,idserv=self.ID,idrole=i.id)
        db.close()

    @asyncio.coroutine
    def restorerolemember(self,client,srv,member):
        db = Database()
        cur = db.execute("SELECT id_role FROM keeprole WHERE id_server = %(idserv)s AND id_member = %(idmemb)s;",idserv=self.ID,idmemb=member.id)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to restore roles of the member")
        ls = []
        for i in cur:
            ls.append(discord.utils.get(srv.roles,id=i[0]))
        yield from client.add_roles(member,ls)
        for i in ls:
            db.call("restorerolemember",idmemb=member.id,idserv=self.ID,idrole=i.id)
        db.close()

    def addkeeprole(self,roleid):
        db = Database()
        db.call("addrole",idserv=self.ID,idrole=roleid)
        db.close()

    def removekeeprole(self,roleid):
        db = Database()
        db.call("removerole",idserv=self.ID,idrole=roleid)
        db.close()

    def get_warned(self):
        db = Database()
        cur = db.execute("SELECT id_member,warn_number FROM warn WHERE id_server = %(idserv)s ORDER BY warn_number;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find warn for this server")
        ls = cur.fetchall()
        db.close()
        return ls

    def get_warnconfig(self):
        db = Database()
        cur = db.execute("SELECT warn_number,sanction FROM warnconfig WHERE id_server = %(idserv)s ORDER BY warn_number;",idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find warnconfig for this server")
        ls = cur.fetchall()
        db.close()
        return ls

    def warnconfig(self,nbr,act):
        db = Database()
        db.call("warnconfigure",idserv=self.ID,warns=nbr,action=act)
        db.close()

    def warnuser(self,memberid):
        db = Database()
        db.call("warnuser",idmemb=memberid,idserv=self.ID)
        db.close()

    def unwarnuser(self,memberid):
        db = Database()
        db.call("unwarnuser",idmemb=memberid,idserv=self.ID)
        db.close()

    def remove(self):
        db = Database()
        db.call("removeserver",idserv=self.ID)
        db.close()

    def getJDR(self,channelid):
        return DBJDR(self.ID,channelid)

def addserver(server):
    db = Database()
    db.call("addserver",idserv=server.id)
    db.close()
    return DBServer(server.id)

def purgeservers(days_):
    db = Database()
    db.call("purgeserver",days=days_)
    db.close()

class DBJDR:
    def __init__(self,srvid,channelid):
        self.server = srvid
        self.channel = channelid
        db = Database()
        cur = db.call("get_jdr",idserv=srvid,idchan=channelid)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the JDR")
        info = cur.fetchone()
        db.close()
        self.creation_date = info[2]
        self.pjs = info[3]
        self.mj = info[4]

    def delete(self):
        db = Database()
        db.call("jdrdelete",idserv=self.server,idchan=self.channel)
        db.close()

    def MJtransfer(self,member_id):
        db = Database()
        db.call("mjtransfer",idserv=self.server,idchan=self.channel,mj=member_id)
        db.close()

    def copy(self,channel_id):
        db = Database()
        db.call("jdrcopy",idserv=self.server,src=self.channel,dest=channel_id)
        db.close()

    def charcreate(self,chardbkey):
        db = Database()
        db.call("charcreate",dbkey=chardbkey,idserv=self.server,idchan=self.channel)
        db.close()

    def extend(self,channel_id):
        db = Database()
        db.call("JDRextend",idserv=self.server,src=self.channel,target=channel_id)
        db.close()

    def unextend(self,channel_id):
        db = Database()
        db.call("JDRstopextend",idserv=self.server,src=self.channel,target=channel_id)
        db.close()

    def unextend_all(self):
        db = Database()
        db.call("JDRstopallextend",idserv=self.server,src=self.channel)
        db.close()

    def get_character(self,charkey):
        db = Database()
        cur = db.call("get_character",dbkey=charkey,idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find character")
        rawchar = cur.fetchone()
        db.close()
        stat = [rawchar[19],rawchar[24],rawchar[22],rawchar[20],rawchar[21],rawchar[23],rawchar[25]]
        if rawchar[28].upper() == "O":
            gm = 0
        else:
            gm = 1
        if rawchar[29].upper() == "O":
            gmdefault = 0
        else:
            gmdefault = 1
        inv = Inventory()
        inv.loadfromdb(rawchar[30])
        char = Character({"charkey":rawchar[0],"name":rawchar[1],"lore":rawchar[2],"lvl":rawchar[3],"PV":rawchar[4],"PVm":rawchar[5],"PM":rawchar[6],"PMm":rawchar[7],"force":rawchar[8],"esprit":rawchar[9],
                          "charisme":rawchar[10],"furtivite":rawchar[11],"karma":rawchar[12],"default_karma":rawchar[13],"money":rawchar[14],"lp":rawchar[15],"dp":rawchar[16],
                          "intuition":rawchar[17],"mentalhealth":rawchar[18],"stat":stat,"mod":gm,"default_mod":gmdefault,"inventory":inv,"linked":rawchar[31]})
        char.bind(self)
        return char

    def charlist(self):
        db = Database()
        cur = db.call("get_allcharacter",idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find character")
        ls = []
        for i in cur:
            ls.append(i[0])
        db.close()
        return ls

    def get_charbase(self):
        ls = self.charlist()
        charbase = {}
        for i in ls:
            charbase[i] = self.get_character(i)
        return charbase

    def get_serverinfo(self):
        return DBServer(self.server)

class BDMember:
    def __init__(self,ID):
        self.ID = ID
        db = Database()
        cur = db.execute("SELECT * FROM Membre WHERE id_member = %(idmemb)s;",idmemb=ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the member")
        info = cur.fetchone()
        db.close()
        self.perm = info[1]

    def is_owner(self):
        return self.perm.upper() == "O"

    def is_manager(self):
        return self.perm.upper() == "M"

    def is_premium(self):
        return self.perm.upper() != "N"

def grantuser(memberid,permcode):
    db = Database()
    db.call("grantperms",idmemb=memberid,perm=permcode)
    db.close()
