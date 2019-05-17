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
import logging,sys,asyncio
import subprocess as sub

class BotManage(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_botowner)
    @commands.command(aliases=["eval"])
    async def debug(self,ctx,*,arg):
        self.logger.log(logging.DEBUG+1,"running debug instruction : %s",arg.replace("```python","").replace("```",""))
        exec(arg.replace("```python","").replace("```",""))

    @commands.check(check_botowner)
    @commands.command()
    async def setgame(self,ctx,*,game):
        global statut
        statut = discord.Game(name=game)
        await self.bot.change_presence(activity=statut)

    @commands.check(check_botowner)
    @commands.command()
    async def setbotmanager(self,ctx,user):
        grantuser(user,'M')
        self.logger.warning("Granted botmanager rights to : %s",user)
        await ctx.message.channel.send("The ID has been set as botmanager succesful")

    @commands.check(check_botowner)
    @commands.command()
    async def setpremium(self,ctx,user):
        grantuser(user,'P')
        self.logger.info("Granted premium rights to : %s",user)
        await ctx.message.channel.send("The ID has been set as premium succesful")

    @commands.check(check_botmanager)
    @commands.command()
    async def blacklist(self,ctx,user,*,reason):
        blacklist(user,reason)
        self.logger.info("blacklisted user %s by %s",user,str(ctx.message.author))
        await ctx.message.channel.send("The following id has been blacklisted : `{}` for\n```\n{}\n```".format(user,reason))

    @commands.check(check_botmanager)
    @commands.command()
    async def unblacklist(self,ctx,user):
        mb = None
        try: mb = DBMember(user)
        except: pass
        if mb is not None:
            mb.unblacklist()
            self.logger.info("unblacklisted user %s by %s",user,str(ctx.message.author))
            await ctx.message.channel.send("The following id has been unblacklisted : `{}`".format(user))

    @commands.check(check_botmanager)
    @commands.command()
    async def purgeserver(self,ctx,days: int):
        nbr = purgeservers(days)
        self.logger.warning("purged servers older than %d days requested by %s",days,str(ctx.message.author))
        self.logger.info("purged %d servers",nbr)
        await ctx.message.channel.send("Purged servers successful")

    @commands.check(check_botmanager)
    @commands.command()
    async def shutdown(self,ctx):
        await ctx.message.channel.send("You are requesting a shutdown, please ensure that you want to performe it by typing `confirm`")
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
        try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send("your request has timeout")
        else:
            self.logger.warning("Shutdown requested by %s",str(ctx.message.author))
            await self.bot.logout()
            sys.exit(0)

    @commands.check(check_botmanager)
    @commands.command()
    async def reboot(self,ctx):
        await ctx.message.channel.send("You are requesting a reboot, please ensure that you want to performe it by typing `confirm`")
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
        try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send("your request has timeout")
        else:
            self.logger.warning("Reboot requested by %s",str(ctx.message.author))
            await self.bot.logout()
            sub.call(['./bootbot.sh'])
            sys.exit(0)
