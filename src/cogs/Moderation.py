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

from src.utils.checks import *
from src.tools.BotTools import *
from discord.ext import commands
import logging, asyncio
import discord
import typing
from src.tools.Translator import *

class Moderation(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_admin)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command(aliases=['prefix'])
    async def setprefix(self, ctx, pref):
        """**Admin only**
        Set the prefix used by the bot for the command on your server"""
        data = await GenericCommandParameters(ctx)
        role = discord.utils.get(ctx.author.roles, id=data.srv.adminrole)
        await data.srv.setprefix(pref, ctx.author.id, role.id if role is not None else None)
        self.logger.info("Changing command prefix on server %d into '%s'", ctx.message.guild.id, pref)
        await ctx.message.channel.send(data.lang["setprefix"].format(pref))

    @commands.check(check_admin)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.command(aliases=['adminrole'])
    async def setadminrole(self, ctx, role: discord.Role):
        """**Admin only**
        Define or change the role designed as Admin of the bot for your server
        All members with this role will be able to use every command specified as 'Admin' commands.
        Be sure of what you are doing before granting permissions to someone else.
        Even if the owner doesn't have the role, he will be able to use 'Admin' specified commands"""
        data = await GenericCommandParameters(ctx)
        adminrole = discord.utils.get(ctx.author.roles, id=data.srv.adminrole)
        await data.srv.setadminrole(role.id, adminrole.id if adminrole is not None else None)
        self.logger.info("Changing adminrole on server %d", ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["setadmin"].format(role.mention))
