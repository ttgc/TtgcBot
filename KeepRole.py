#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#KeepRoleManager

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

from PythonBDD import *
from INIfiles import *
from converter import *
import discord
import asyncio

def Deprecated(cl):
    print("Deprecated usage of : "+str(cl))

@Deprecated
class KeepRoleServer:
    def __init__(self,servID):
        self.id = servID
        self.roles = []
        self.enabled = False
        self.members = {}
        kr = BDD("keeprole")
        kr.load()
        servls = convert_str_into_ls_spe(kr["servers","list"])
        if str(self.id) in servls:
            self.enabled = str(self.id) in convert_str_into_ls_spe(kr["servers","enabled"])
            self.roles = convert_str_into_ls_spe(kr["roles",str(self.id)])
            self.members = convert_str_into_dict_with_ls_spe(kr["members",str(self.id)])
        self._system = kr

    def switch(self):
        self.enabled = not self.enabled
        srvls = convert_str_into_ls_spe(self._system["servers","list"])
        if str(self.id) not in srvls:
            srvls = convert_str_into_ls_spe(self._system["servers","list"])
            srvls.append(str(self.id))
            self._system["servers","list"] = convert_ls_into_str_spe(srvls)
            self._system["members",str(self.id)] = str(self.members)
            self._system["roles",str(self.id)] = convert_ls_into_str_spe(self.roles)
        enls = convert_str_into_ls_spe(self._system["servers","enabled"])
        if self.enabled:
            enls.append(str(self.id))
            self._system["servers","enabled"] = convert_ls_into_str_spe(enls)
        else:
            enls.remove(str(self.id))
            self._system["servers","enabled"] = convert_ls_into_str_spe(enls)
        self._system.save()

    def setroles(self,ls):
        self.roles = list(ls)
        srvls = convert_str_into_ls_spe(self._system["servers","list"])
        if str(self.id) not in srvls:
            srvls = convert_str_into_ls_spe(self._system["servers","list"])
            srvls.append(str(self.id))
            self._system["servers","list"] = convert_ls_into_str_spe(srvls)
            self._system["members",str(self.id)] = str(self.members)
            enls = convert_str_into_ls_spe(self._system["servers","enabled"])
            if self.enabled:
                enls.append(str(self.id))
                self._system["servers","enabled"] = convert_ls_into_str_spe(enls)
        self._system["roles",str(self.id)] = convert_ls_into_str_spe(self.roles)
        self._system.save()

    def addroles(self,ls):
        self.setroles(self.roles+ls)

    def removeroles(self,ls):
        nbr = len(ls)
        for i in ls:
            try:
                self.roles.remove(i)
            except ValueError:
                nbr -= 1
        self.setroles(self.roles)
        return nbr

    def setmembers(self,dic):
        self.members = dict(dic)
        srvls = convert_str_into_ls_spe(self._system["servers","list"])
        if str(self.id) not in srvls:
            srvls = convert_str_into_ls_spe(self._system["servers","list"])
            srvls.append(str(self.id))
            self._system["servers","list"] = convert_ls_into_str_spe(srvls)
            enls = convert_str_into_ls_spe(self._system["servers","enabled"])
            if self.enabled:
                enls.append(str(self.id))
                self._system["servers","enabled"] = convert_ls_into_str_spe(enls)
            self._system["roles",str(self.id)] = convert_ls_into_str_spe(self.roles)
        self._system["members",str(self.id)] = str(self.members)
        self._system.save()

    def addmembers(self,dic):
        for i in dic.keys():
            self.members[i] = dic[i]
        self.setmembers(self.members)

    def removemembers(self,ls):
        nbr = len(ls)
        for i in ls:
            try:
                del(self.members[i])
            except KeyError:
                nbr -= 1
        self.setmembers(self.members)
        return nbr

    @asyncio.coroutine
    def apply(self,client):
        srv = client.get_server(self.id)
        for i in self.members.keys():
            mb = srv.get_member(i)
            if mb is not None:
                for k in self.members[i]:
                    rl = discord.utils.get(srv.roles,id=k)
                    yield from client.add_roles(mb,rl)
                self.removemembers(i)
