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

import discord
import asyncio
from src.utils.DatabaseManager import *
import src.tools.Character as ch
import src.tools.CharacterUtils as chutil

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
        self.mjrole = info[1] if info[1] is not None else "-1"
        self.prefix = info[2]
        self.keepingrole = info[3]
        self.adminrole = info[4] if info[4] is not None else "-1"

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
        cur = db.execute("SELECT id_role FROM role WHERE id_server = %(idserv)s GROUP BY id_role;",idserv=self.ID)
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
            todel = []
            for i in ls:
                if i[0] in extended:
                    todel.append(i)#ls.remove(i)
            for i in todel:
                ls.remove(i)
        db.close()
        return ls

    def jdrextension(self):
        db = Database()
        cur = db.execute("SELECT id_target FROM JDRextension WHERE id_server = %(idserv)s GROUP BY id_target;",idserv=self.ID)
        if cur is not None:
            extended = []
            for i in cur:
                extended.append(i[0])
        db.close()
        return extended

    def blockword(self,string):
        db = Database()
        db.call("blockword",idserv=self.ID,word=string)
        db.close()

    def unblockword(self,string):
        db = Database()
        db.call("unblockword",idserv=self.ID,word=string)
        db.close()

    def blockusername(self,user):
        db = Database()
        cur = db.call("userblock",usr=user,idserv=self.ID)
        newid = None
        if cur is not None:
            newid = cur.fetchone()
        db.close()
        return newid

    def unblockusername(self,user):
        db = Database()
        cur = db.call("find_userblocked",usr=user,idserv=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("Unable to unblock username")
        usrid = cur.fetchone()[0]
        if usrid is None:
            db.close(True)
            return False
        db.close()
        db = Database()
        db.call("userunblock",id=usrid)
        db.close()
        return True

    def blockuserlist(self):
        db = Database()
        cur = db.call("userblock_list",idserv=self.ID)
        if cur is None:
            db.close(True)
            return []
        ls = []
        for i in cur:
            ls.append(i)
        db.close()
        return ls

    def backuprolemember(self,member):
        db = Database()
        ls = self.keeprolelist()
        for i in member.roles:
            if str(i.id) in ls:
                db.call("backuprolemember",idmemb=str(member.id),idserv=self.ID,idrole=str(i.id))
        db.close()

    async def restorerolemember(self,srv,member):
        db = Database()
        cur = db.execute("SELECT id_role FROM keeprole WHERE id_server = %(idserv)s AND id_member = %(idmemb)s;",idserv=self.ID,idmemb=member.id)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to restore roles of the member")
        ls = []
        for i in cur:
            rl = discord.utils.get(srv.roles,id=int(i[0]))
            ls.append(rl)
            await member.add_roles(rl)
        for i in ls:
            db.call("restorerolemember",idmemb=str(member.id),idserv=self.ID,idrole=str(i.id))
        db.close()

    def addkeeprole(self,roleid):
        db = Database()
        db.call("addrole",idserv=self.ID,idrole=roleid)
        db.close()

    def removekeeprole(self,roleid):
        db = Database()
        db.call("removerole",idserv=self.ID,idrole=roleid)
        db.close()

    def clearkeeprole(self):
        db = Database()
        db.call("clearkeeprole",idserv=self.ID)
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

    def get_warnnbr(self,dbmember):
        db = Database()
        cur = db.execute("SELECT warn_number FROM warn WHERE id_server = %(idserv)s AND id_member = %(idmemb)s;",idserv=self.ID,idmemb=dbmember.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find warn number for this server and user")
        result = cur.fetchone()
        db.close()
        if result is None: return 0
        return result[0]

    def get_warnconfig(self):
        db = Database()
        cur = db.execute("SELECT warn_number,sanction FROM warnconfig WHERE id_server = %(idserv)s ORDER BY warn_number DESC;",idserv=self.ID)
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

    def jdrstart(self,channelid,mjid):
        db = Database()
        db.call("jdrcreate",idserv=self.ID,idchan=channelid,mj=mjid)
        db.close()
        return self.getJDR(channelid)

def addserver(server):
    db = Database()
    db.call("addserver",idserv=str(server.id))
    db.close()
    return DBServer(str(server.id))

def purgeservers(days_):
    db = Database()
    cur = db.call("purgeserver",days=days_)
    if cur is None:
        db.close(True)
        raise DatabaseException("unable to purge servers")
    nbr = cur.fetchone()[0]
    db.close()
    return int(nbr)

def srvlist():
    db = Database()
    cur = db.execute("SELECT id_server FROM Serveur WHERE id_server NOT IN (SELECT id_server FROM purge)")
    if cur is None:
        db.close(True)
        raise DatabaseException("unable to find the server list")
    ls = []
    for i in cur:
        ls.append(i[0])
    db.close()
    return ls

class DBJDR:
    def __init__(self,srvid,channelid):
        self.server = srvid
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
        self.channel = info[1]

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

    def charcreate(self,chardbkey,idclass):
        db = Database()
        db.call("charcreate",dbkey=chardbkey,idserv=self.server,idchan=self.channel,cl=idclass)
        db.close()

    def chardelete(self,chardbkey):
        db = Database()
        db.call("chardelete",dbkey=chardbkey,idserv=self.server,idchan=self.channel)
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
        gm = ch.Character.gm_map_chartoint[rawchar[28].upper()]
        gmdefault = ch.Character.gm_map_chartoint[rawchar[29].upper()]
        inv = chutil.Inventory()
        inv.loadfromdb(rawchar[30])
        pets = {}
        db = Database()
        cur = db.call("get_pets",dbkey=rawchar[0],idserv=self.server,idchan=self.channel)
        if cur is not None:
            for i in cur:
                gmpet = ch.Character.gm_map_chartoint[i[24].upper()]
                gmpetdefault = ch.Character.gm_map_chartoint[i[25].upper()]
                pets[i[0]] = ch.Pet(petkey=i[0],charkey=rawchar[0],name=i[1],espece=i[2],
                                    PVm=i[5],PMm=i[7],force=i[8],esprit=i[9],
                                    charisme=i[10],agilite=i[11],karma=i[12],
                                    stat=[i[14],i[19],i[17],i[15],i[16],i[18],i[20]],mod=gmpet,
                                    PV=i[4],PM=i[6],default_mod=gmpetdefault,
                                    instinct=i[13],lvl=i[3],prec=i[26],luck=i[27])
        db.close()
        db = Database()
        cur = db.call("get_skill",dbkey=rawchar[0],idserv=self.server,idchan=self.channel)
        skls = []
        if cur is not None:
            for i in cur:
                skls.append(chutil.Skill(i[0]))
        db.close()
        char = ch.Character(charkey=rawchar[0],name=rawchar[1],lore=rawchar[2],
                            lvl=rawchar[3],PV=rawchar[4],PVm=rawchar[5],PM=rawchar[6],
                            PMm=rawchar[7],force=rawchar[8],esprit=rawchar[9],
                            charisme=rawchar[10],furtivite=rawchar[11],karma=rawchar[12],
                            default_karma=rawchar[13],money=rawchar[14],lp=rawchar[15],
                            dp=rawchar[16],intuition=rawchar[17],mentalhealth=rawchar[18],
                            stat=stat,mod=gm,default_mod=gmdefault,inventory=inv,
                            linked=rawchar[31],pet=pets,skills=skls,dead=rawchar[32],
                            classe=rawchar[33],selected=rawchar[34],xp=rawchar[35],
                            prec=rawchar[36],luck=rawchar[37],
                            org=chutil.retrieveOrganization(rawchar[38]),
                            hybrid=rawchar[39], symbiont=rawchar[40],
                            planet_pilot=rawchar[41], astral_pilot=rawchar[42])
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
        charbase = []
        for i in ls:
            charbase.append(self.get_character(i))
        return charbase

    def get_serverinfo(self):
        return DBServer(self.server)

    def set_finalizer_field(self,title,content):
        db = Database()
        db.call("set_finalize_field",idserv=self.server,idchan=self.channel,titl=title,descr=content)
        db.close()

    def del_finalizer_field(self,title):
        db = Database()
        db.call("del_finalize_field",idserv=self.server,idchan=self.channel,titl=title)
        db.close()

    def get_finalizer(self):
        db = Database()
        cur = db.call("finalizer",idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close()
            return []
        ls = []
        for i in cur:
            ls.append((i[2],i[3]))
        db.close()
        return ls

    def get_group(self, name):
        return DBJDRGroup(name, self.server, self.channel)

    def get_all_groupkeys(self):
        db = Database()
        cur = db.execute("SELECT grkey WHERE id_server = %(idsrv)s AND id_channel = %(idchan)s;", idsrv=self.server, idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to fetch all groups keys")
        ls = []
        for i in cur:
            ls.append(i[0])
        db.close()
        return ls

    def get_all_groups(self):
        keys = self.get_all_groupkeys()
        ls = []
        for i in keys:
            ls.append(self.get_group(i))
        return ls

    def add_group(self, name):
        db = Database()
        db.call("add_group", dbkey=name, idserv=self.server, idchan=self.channel)
        db.close()
        return self.get_group(name)

    def group_exists(self, name):
        db = Database()
        cur = db.execute("SELECT COUNT(*) FROM JDR_Groupe WHERE grkey = %(key)s AND id_server = %(idsrv)s AND id_channel = %(idchan)s;", key=name, idsrv=self.server, idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("Unable to check if the JDR group exists or not")
        nbr = int(cur.fetchone())
        return nbr > 0

class DBJDRGroup:
    def __init__(self, name, srvid, channelid):
        self.server = srvid
        self.channel = channelid
        self.name = name
        db = Database()
        cur = db.execute("SELECT localMJ, joinable FROM JDR_Groupe WHERE grkey = %(key)s AND id_server = %(idsrv)s AND id_channel = %(idchan)s;", key=name, idsrv=srvid, idchan=channelid)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the JDR Group")
        info = cur.fetchone()
        db.close()
        self.localMJ = info[0]
        self.joinable = info[1]
        self._member_cache = []
        self._should_reload_cache = True

    def edit(self, localMJ = None, joinable = None):
        localMJ = self.localMJ if localMJ is None else localMJ
        joinable = self.joinable if joinable is None else joinable
        db = Database()
        db.call("update_group", dbkey=self.name, idserv=self.server, idchan=self.channel, overrideMJ=localMJ, groupisjoinable=joinable)
        db.close()

    def delete(self):
        db = Database()
        db.call("delete_group", dbkey=self.name, idserv=self.server, idchan=self.channel)
        db.close()

    def join(self, charkey):
        db = Database()
        db.call("join_group", grp=self.name, idserv=self.server, idchan=self.channel, charact=charkey)
        db.close()
        self._should_reload_cache = True

    def leave(self, charkey):
        db = Database()
        db.call("leave_group", grp=self.name, idserv=self.server, idchan=self.channel, charact=charkey)
        db.close()
        self._should_reload_cache = True

    def fetch_members(self, force=False):
        if not self._should_reload_cache and not force: return self._member_cache
        db = Database()
        cur = db.execute("SELECT charkey FROM JDR_Groupe_Member WHERE grkey = %(key)s AND id_server = %(idsrv)s AND id_channel = %(idchan)s;", key=self.name, idsrv=self.server, idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to fetch members of the JDR Group")
        self._member_cache = []
        for i in cur:
            self._member_cache.append(i[0])
        db.close()
        self._should_reload_cache = False
        return self._member_cache

    def is_member(self, charkey, force_reload=False):
        members = self.fetch_members(force_reload)
        return charkey in members

class DBMember:
    def __init__(self,ID):
        self.ID = ID
        db = Database()
        cur = db.execute("SELECT * FROM Membre WHERE id_member = %(idmemb)s;",idmemb=ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to find the member")
        info = cur.fetchone()
        if info is None:
            db.close(True)
            raise DatabaseException("unexisting member")
        db.close()
        self.perm = info[1]

    def is_owner(self):
        return self.perm.upper() == "O"

    def is_manager(self):
        return (self.perm.upper() == "M" or self.is_owner())

    def is_premium(self):
        return self.perm.upper() != "N"

    def is_blacklisted(self):
        db = Database()
        cur = db.execute("SELECT COUNT(*) FROM blacklist WHERE id_member = %(idmemb)s;",idmemb=self.ID)
        if cur is None:
            db.close(True)
            raise DatabaseException("unable to retrieve blacklisting")
        blacklisted = True
        if cur.fetchone()[0] == 0:
            blacklisted = False
        db.close()
        rs = ""
        if blacklisted:
            db = Database()
            cur = db.execute("SELECT reason FROM blacklist WHERE id_member = %(idmemb)s;",idmemb=self.ID)
            if cur is None:
                db.close(True)
                raise DatabaseException("unable to find reason for blacklisting")
            rs = cur.fetchone()[0]
            db.close()
        return blacklisted,rs

    def unblacklist(self):
        if not self.is_blacklisted()[0]: return
        db = Database()
        db.call("switchblacklist",idmemb=self.ID,eventual_reason="")
        db.close()

def grantuser(memberid,permcode):
    db = Database()
    db.call("grantperms",idmemb=memberid,perm=permcode)
    db.close()

def blacklist(memberid,reason):
    try:
        mb = DBMember(memberid)
        if mb.is_blacklisted()[0]: return
    except DatabaseException: pass
    db = Database()
    db.call("switchblacklist",idmemb=memberid,eventual_reason=reason)
    db.close()
    return DBMember(memberid)

def setuserlang(memberid,lang):
    db = Database()
    db.call("setlang",idmemb=memberid,lg=lang.upper())
    db.close()

def getuserlang(memberid):
    db = Database()
    cur = db.call("getlang",idmemb=memberid)
    lang = cur.fetchone()[0]
    db.close()
    return lang
