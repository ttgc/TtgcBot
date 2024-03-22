#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2024  Thomas PIOT
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
from ..common.contextext import ExtendedContext


def check_server_owner(ctx: ExtendedContext) -> bool:
    return ctx.guild and ctx.guild.owner == ctx.author # type: ignore


async def check_server_admin(ctx: ExtendedContext) -> bool:
    if check_server_owner(ctx):
        return True

    srv = await ctx.ext.server

    return isinstance(ctx.author, discord.Member) and srv.admin_role and ctx.author.get_role(srv.admin_role) # type: ignore


async def check_mj(ctx: ExtendedContext) -> bool:
    srv = await ctx.ext.server

    if not srv.mj_role:
        return await check_server_admin(ctx)

    return isinstance(ctx.author, discord.Member) and srv.mj_role and ctx.author.get_role(srv.mj_role) # type: ignore
