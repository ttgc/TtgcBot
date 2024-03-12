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


import sys
import discord
from discord.ext import commands
from config import Log, Config, Environment, LogConfig


class BotManage(commands.Cog, name="Bot Management", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot) -> None:
        self.bot = client
        self.status = self.bot.activity

    @commands.is_owner()
    @commands.command(aliases=["eval"], enabled=Config().env != Environment.PROD)
    async def debug(self, ctx: commands.Context, *, arg: str) -> None:
        instruction = arg.replace("```python", "").replace("```py", "").replace("```", "")
        Log.debug("running debug instruction : %s", instruction)
        exec(instruction)
        logfiles = [discord.File(cfg.filepath) for cfg in LogConfig.load_all()]
        await ctx.author.send('Debug finished. Here are the logs:', files=logfiles)
        Log.debug("sent logs to %d", ctx.author)

    @commands.is_owner()
    @commands.command()
    async def setgame(self, ctx: commands.Context, *, game: str) -> None:
        self.status = discord.Game(name=game)
        await self.bot.change_presence(activity=self.status)

    @commands.is_owner()
    @commands.command()
    async def shutdown(self, ctx: commands.Context) -> None:
        await ctx.send("You are requesting a shutdown, please ensure that you want to performe it by typing `confirm`")
        chk = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'
        answer = await self.bot.wait_for('message', check=chk, timeout=60)

        if not answer:
            await ctx.send("your request has timeout")
        else:
            Log.warn("Shutdown requested by %s", ctx.author)
            await self.bot.close()
            sys.exit(0)
