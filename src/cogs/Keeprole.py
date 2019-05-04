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

from src.checks import *
from src.BotTools import *
from discord.ext import commands
import logging,asyncio
import discord
from src.Translator import *

class Keeprole(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_admin)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.group(invoke_without_command=False, aliases=['kr'])
    async def keeprole(self,ctx): pass

    @commands.cooldown(1,30,commands.BucketType.guild)
    @keeprole.command(name="enabled",aliases=['switch'])
    async def keeprole_enabled(self,ctx):
        data = GenericCommandParameters(ctx)
        data.srv.togglekeeprole()
        self.logger.info("Toggle Keeprole system on server %s",str(ctx.message.guild.id))
        if not data.srv.keepingrole:
            await ctx.message.channel.send(data.lang["kr_on"])
        else:
            await ctx.message.channel.send(data.lang["kr_off"])

    @commands.cooldown(1,3600,commands.BucketType.guild)
    @keeprole.command(name="clear")
    async def keeprole_clear(self,ctx):
        data = GenericCommandParameters(ctx)
        data.srv.clearkeeprole()
        self.logger.info("purged keeprole on server %s",str(ctx.message.guild.id))
        await ctx.message.channel.send(data.lang["kr_purge"])

    @keeprole.group(name="roles",invoke_without_command=True)
    async def keeprole_roles(self,ctx):
        await self.keeprole_roles_list(ctx)

    @keeprole_roles.command(name="list")
    async def keeprole_roles_list(self,ctx):
        data = GenericCommandParameters(ctx)
        ls = srv.keeprolelist()
        rllist = ""
        for i in ls:
            rllist += "{}\n".format(discord.utils.get(ctx.message.guild.roles,id=int(i)).mention)
        embd = discord.Embed(title="Keeprole system",description=data.lang["kr_roles"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.add_field(name="Roles list :",value=rllist,inline=True)
        await ctx.message.channel.send(embed=embd)

    @keeprole_roles.command(name="add",aliases="+")
    async def keeprole_roles_add(self,ctx,roles: commands.Greedy[discord.Role]):
        data = GenericCommandParameters(ctx)
        info = await self.bot.application_info()
        botmember = ctx.message.guild.get_member(info.id)
        strls = ""
        for i in roles:
            if i.position < botmember.top_role.position:
                strls += "\n{}".format(i.mention)
                data.srv.addkeeprole(str(i.id))
        self.logger.info("added %d roles to keeprole on server %s",len(roles),str(ctx.message.guild.id))
        await ctx.message.channel.send(data.lang["kr_add"].format(strls))

    @keeprole_roles.command(name="delete",aliases=["-","del","remove","rm"])
    async def keeprole_roles_delete(self,ctx,roles: commands.Greedy[discord.Role]):
        data = GenericCommandParameters(ctx)
        info = await self.bot.application_info()
        botmember = ctx.message.guild.get_member(info.id)
        strls = ""
        for i in roles:
            if i.position < botmember.top_role.position:
                strls += "\n{}".format(i.mention)
                data.srv.removekeeprole(str(i.id))
        self.logger.info("removed %d roles from keeprole on server %s",len(roles),str(ctx.message.guild.id))
        await ctx.message.channel.send(data.lang["kr_del"].format(strls))

    @keeprole.group(name="members",invoke_without_command=True)
    async def keeprole_members(self,ctx):
        await self.keeprole_members_list(ctx)

    @keeprole_members.command(name="list")
    async def keeprole_members_list(self,ctx):
        data = GenericCommandParameters(ctx)
        ls = data.srv.keeprolememberwithrole()
        mblist = {}
        for i in ls:
            if i[0] not in mblist:
                mblist[i[0]] = []
            mblist[i[0]].append(i[1])
        embd = discord.Embed(title="Keeprole system",description=data.lang["kr_members"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        for i,k in mblist.items():
            rllist = ""
            for j in k:
                rllist += "{}\n".format(discord.utils.get(ctx.message.guild.roles,id=int(j)).mention)
            user = await self.bot.get_user(int(i))
            embd.add_field(name="{} :".format(str(user)),value=rllist,inline=True)
        await ctx.message.channel.send(embed=embd)
