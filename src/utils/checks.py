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

from src.tools.BotTools import *
from src.tools.Translator import *
from src.utils.exceptions import APIException
import discord.utils

async def is_blacklisted(ID):
    try: member = await DBMember(ID)
    except: return False, ""
    bl, rs = member.is_blacklisted()
    return bl, rs

async def is_botmanager(ID):
    try: member = await DBMember(ID)
    except: return False
    return member.is_manager()

async def is_premium(ID):
    try: member = await DBMember(ID)
    except: return False
    return member.is_premium()

async def is_owner(ID):
    try: member = await DBMember(ID)
    except: return False
    return member.is_owner()

async def check_admin(ctx):
    srv = await DBServer(ctx.message.guild.id)
    return discord.utils.get(ctx.message.guild.roles, id=srv.adminrole) in ctx.message.author.roles or ctx.message.author == ctx.message.guild.owner

async def check_botmanager(ctx):
    result = await is_botmanager(ctx.message.author.id)
    return result

async def check_botowner(ctx):
    result = await is_owner(ctx.message.author.id)
    return result

async def check_premium(ctx):
    result = await is_premium(ctx.message.author.id)
    return result

async def check_mj(ctx):
    srv = await DBServer(ctx.message.guild.id)
    return discord.utils.get(ctx.message.guild.roles, id=srv.mjrole) in ctx.message.author.roles

async def check_jdrchannel(ctx):
    srv = await DBServer(ctx.message.guild.id)

    role = discord.utils.get(ctx.author.roles, id=srv.mjrole)
    if role is None: role = discord.utils.get(ctx.author.roles, id=srv.adminrole)
    jdrlist = await srv.jdrlist(ctx.author.id, role.id if role is not None else None)

    for i in jdrlist:
        if ctx.channel.id == i.get("channel", -1): return True
        if ctx.channel.id in i.get("extensions", []): return True
    return False

async def check_chanmj(ctx):
    jdrchannel = await check_jdrchannel(ctx)

    if jdrchannel:
        role = discord.utils.get(ctx.author.roles, id=srv.mjrole)
        if role is None: role = discord.utils.get(ctx.author.roles, id=srv.adminrole)

        try:
            jdr = await DBJDR(ctx.message.guild.id, ctx.message.channel.id, ctx.author.id, role.id if role is not None else None)
            return ctx.message.author.id == jdr.mj
        except APIException as e:
            if e["code"] != 404: raise e

    return False

class GenericCommandParameters:
    async def __init__(self, ctx):
        self.ID = ctx.message.id
        self.srv = await DBServer(ctx.message.guild.id)
        role = discord.utils.get(ctx.author.roles, id=srv.mjrole)
        if role is None: role = discord.utils.get(ctx.author.roles, id=srv.adminrole)
        lgcode = await DBMember.getuserlang(ctx.message.author.id)
        if not lang_exist(lgcode): lgcode = "EN"
        self.lang = get_lang(lgcode)
        self.jdrlist = await self.srv.jdrlist(ctx.author.id, role.id if role is not None else None)
        self.jdr = None
        self.charbase = None
        self.char = None
        jdrchannel = await check_jdrchannel(ctx)
        if jdrchannel:
            self.jdr = await self.srv.getJDR(ctx.message.channel.id, ctx.author.id, role.id if role is not None else None)
            self.charbase = await self.jdr.charlist()
            for i in self.charbase.get("linked", []):
                if i.get("member", -1) == ctx.message.author.id and i.get("selected", False):
                    self.char = await self.jdr.get_character(i.get("charkey", ""))
                    break

async def check_haschar(ctx):
    data = await GenericCommandParameters(ctx)
    return data.char is not None
