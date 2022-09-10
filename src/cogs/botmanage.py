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

#from utils.checks import check_botowner
from discord.ext import commands
from setup.loglevel import LogLevel
import sys
import asyncio
import discord

# Temp: Remove it after checks rewrite
check_botmanager = check_botowner = lambda ctx: True

class BotManage(commands.Cog, name="Bot Management", command_attrs=dict(hidden=True)):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.handlederror = 0
        self.status = None

    @commands.check(check_botowner)
    @commands.command(aliases=["eval"])
    async def debug(self, ctx, *, arg):
        instruction = arg.replace("```python", "").replace("```py", "").replace("```", "")
        self.logger.log(LogLevel.DEBUG.value, "running debug instruction : %s", instruction)
        exec(instruction)

    @commands.check(check_botowner)
    @commands.command()
    async def setgame(self, ctx, *, game):
        self.status = discord.Game(name=game)
        await self.bot.change_presence(activity=self.status)

    @commands.check(check_botmanager)
    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("You are requesting a shutdown, please ensure that you want to performe it by typing `confirm`")
        chk = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'

        try:
            answer = await self.bot.wait_for('message', check=chk, timeout=60)
        except asyncio.TimeoutError:
            answer = None

        if answer is None:
            await ctx.send("your request has timeout")
        else:
            self.logger.warning("Shutdown requested by %s", ctx.message.author)
            await self.bot.close()
            sys.exit(0)

    @commands.check(check_botmanager)
    @commands.command()
    async def geterrornbr(self,ctx):
        await ctx.message.author.send(f"Handled error since boot : {self.handlederror}")
