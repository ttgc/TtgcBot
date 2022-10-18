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

from models import DBMember, DBServer, DBJDR
from exceptions import APIException
from core.commandparameters import GenericCommandParameters, is_jdrchannel
import discord.utils

async def is_blacklisted(ID):
    try: member = await DBMember(ID)
    except Exception: return False, ""
    bl, rs = member.is_blacklisted()
    return bl, rs

async def is_botmanager(ID):
    try: member = await DBMember(ID)
    except Exception: return False
    return member.is_manager()

async def is_premium(ID):
    try: member = await DBMember(ID)
    except Exception: return False
    return member.is_premium()

async def is_owner(ID):
    try: member = await DBMember(ID)
    except Exception: return False
    return member.is_owner()

async def check_admin(ctx):
    srv = await DBServer(ctx.guild.id)
    return discord.utils.get(ctx.guild.roles, id=srv.adminrole) in ctx.author.roles or ctx.author == ctx.guild.owner

async def check_botmanager(ctx):
    result = await is_botmanager(ctx.author.id)
    return result

async def check_botowner(ctx):
    result = await is_owner(ctx.author.id)
    return result

async def check_premium(ctx):
    result = await is_premium(ctx.author.id)
    return result

async def check_mj(ctx):
    srv = await DBServer(ctx.guild.id)
    return discord.utils.get(ctx.guild.roles, id=srv.mjrole) in ctx.author.roles

async def check_jdrchannel(ctx):
    srv = await DBServer(ctx.guild.id)
    role = discord.utils.get(ctx.author.roles, id=srv.mjrole)
    if role is None: role = discord.utils.get(ctx.author.roles, id=srv.adminrole)
    jdrlist = await srv.jdrlist(ctx.author.id, role.id if role is not None else None)
    return is_jdrchannel(jdrlist, ctx.channel.id)

async def check_chanmj(ctx):
    jdrchannel = await check_jdrchannel(ctx)

    if jdrchannel:
        srv = await DBServer(ctx.guild.id)
        role = discord.utils.get(ctx.author.roles, id=srv.mjrole)
        if role is None: role = discord.utils.get(ctx.author.roles, id=srv.adminrole)

        try:
            jdr = await DBJDR(ctx.guild.id, ctx.channel.id, ctx.author.id, role.id if role is not None else None)
            return ctx.author.id == jdr.mj
        except APIException as e:
            if e["code"] != 404: raise e

    return False

async def check_haschar(ctx):
    data = await GenericCommandParameters.get_from_context(ctx)
    return data.char is not None
