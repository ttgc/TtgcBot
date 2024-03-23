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


from typing import Optional
import discord
from models import MemberPerms
from config import Config
from ..common.contextext import ExtendedContext


async def check_botmanager(ctx: ExtendedContext) -> bool:
    member = await ctx.ext.member
    return member.perms >= MemberPerms.MANAGER if member else False


async def check_premium(ctx: ExtendedContext) -> bool:
    member = await ctx.ext.member
    return member.perms >= MemberPerms.PREMIUM if member else False


def check_subbed(ctx: ExtendedContext) -> bool:
    config = Config()['discord']['sub-guild']
    gid = config['gid']
    role_id = config['sub-role']
    subguild: Optional[discord.Guild] = discord.utils.get(ctx.bot.guilds, id=gid)

    if not subguild:
        return False

    member = subguild.get_member(ctx.author.id)
    return member and member.get_role(role_id) # type: ignore


async def check_subbed_or_premium(ctx: ExtendedContext) -> bool:
    return check_subbed(ctx) or await check_premium(ctx)
