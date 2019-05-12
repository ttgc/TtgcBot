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

from src.BotTools import *
from src.Translator import *
import discord.utils

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

def check_admin(ctx):
    srv = DBServer(str(ctx.message.guild.id))
    return discord.utils.get(ctx.message.guild.roles,id=srv.adminrole) in ctx.message.author.roles or ctx.message.author == ctx.message.guild.owner

def check_botmanager(ctx): return is_botmanager(str(ctx.message.author.id))
def check_botowner(ctx): return is_owner(str(ctx.message.author.id))
def check_premium(ctx): return is_premium(str(ctx.message.author.id))

def check_mj(ctx):
    srv = DBServer(str(ctx.message.guild.id))
    return discord.utils.get(ctx.message.guild.roles,id=int(srv.mjrole)) in ctx.message.author.roles

def check_jdrchannel(ctx):
    srv = DBServer(str(ctx.message.guild.id))
    for i in srv.jdrlist():
        if str(ctx.message.channel.id) == i[0]: return True
    return str(ctx.message.channel.id) in srv.jdrextension()

def check_chanmj(ctx):
    if check_jdrchannel(ctx):
        jdr = DBJDR(str(ctx.message.guild.id),str(ctx.message.channel.id))
        return str(ctx.message.author.id) == jdr.mj
    return False

class GenericCommandParameters:
    def __init__(self,ctx):
        self.ID = str(ctx.message.id)
        self.srv = DBServer(str(ctx.message.guild.id))
        lgcode = getuserlang(str(ctx.message.author.id))
        if not lang_exist(lgcode): lgcode = "EN"
        self.lang = get_lang(lgcode)
        self.jdrlist = self.srv.jdrlist()
        self.jdr = None
        self.charbase = None
        self.char = None
        if check_jdrchannel(ctx):
            self.jdr = self.srv.getJDR(str(ctx.message.channel.id))
            self.charbase = self.jdr.get_charbase()
            for i in self.charbase:
                if i.linked == str(ctx.message.author.id) and i.selected:
                    self.char = i
                    break

def check_haschar(ctx):
    data = GenericCommandParameters(ctx)
    return data.char is not None
