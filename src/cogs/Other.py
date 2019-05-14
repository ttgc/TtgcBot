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
import logging,asyncio,time
import discord
from random import randint,choice
from src.tools.Translator import *

class Other(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.cooldown(1,30,commands.BucketType.user)
    @commands.command()
    async def ping(self,ctx):
        data = GenericCommandParameters(ctx)
        tps_start = time.clock()
        await ctx.message.channel.send(":ping_pong: pong ! :ping_pong:")
        tps_end = time.clock()
        ping = round((tps_end-tps_start)*1000)
        await ctx.message.channel.send(data.lang["ping"].format(ping))
        self.logger.log(logging.DEBUG+1,"current ping : %d ms",ping)

    @commands.cooldown(1,60,commands.BucketType.user)
    @commands.command(aliases=['setlanguage'])
    async def setlang(self,ctx,lg):
        if lang_exist(lg):
            oldlg = getuserlang(str(ctx.message.author.id))
            setuserlang(str(ctx.message.author.id),lg)
            await ctx.message.channel.send(get_lang(lg)["setlang"].format(lg))
            self.logger.info("user %s switched lang from %s to %s",str(ctx.message.author.id),oldlg,lg)
        else:
            data = GenericCommandParameters(ctx)
            await ctx.message.channel.send(data.lang["setlang_notexist"].format(lg))

    @commands.command(aliases=['invit'])
    async def invite(self,ctx):
        data = GenericCommandParameters(ctx)
        botaskperm = discord.Permissions().all()
        botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
        url = discord.utils.oauth_url(str(self.bot.user.id),botaskperm)
        embd = discord.Embed(title="TtgcBot",description=data.lang["invite"],colour=discord.Color(randint(0,int('ffffff',16))),url=url)
        embd.set_footer(text=data.lang["invite_author"],icon_url=self.bot.user.avatar_url)
        embd.set_image(url=self.bot.user.avatar_url)
        embd.set_author(name="Ttgc",icon_url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/08/avatar-2-perso.png",url=url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["invite_srv"],value=str(len(self.bot.guilds))+" servers",inline=True)
        await ctx.message.channel.send(embed=embd)
        self.logger.info("Invite generated on channel %d from server %d by %d",ctx.message.channel.id,ctx.message.guild.id,ctx.message.author.id)

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def yay(self,ctx):
        f = open("pictures/YAY.png","rb")
        await ctx.message.channel.send("YAY !",file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def choquedecu(self,ctx):
        f = open("pictures/choquedecu.png","rb")
        await ctx.message.channel.send("#choquedecu",file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def onichan(self,ctx):
        f = open("pictures/onichan.jpg","rb")
        await ctx.message.channel.send(file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def pi(self,ctx):
        await ctx.message.channel.send("3,141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 105 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 0679...\nhttp://www.nombrepi.com/")

    @commands.cooldown(7,30,commands.BucketType.channel)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def tell(self,ctx,*,msg):
        self.logger.info("%s (%d) said on channel %d from server %d through /tell : %s",ctx.message.author,ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id,msg)
        await ctx.message.channel.send(msg)
        await ctx.message.delete()

    @commands.cooldown(3,30,commands.BucketType.channel)
    @commands.bot_has_permissions(manage_messages=True,send_tts_messages=True)
    @commands.command(aliases=['telltts'])
    async def ttstell(self,ctx,*,msg):
        self.logger.info("%s (%d) said on channel %d from server %d through /ttstell : %s",ctx.message.author,ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id,msg)
        await ctx.message.channel.send(msg,tts=True)
        await ctx.message.delete()

    @commands.cooldown(5,30,commands.BucketType.channel)
    @commands.cooldown(1,10,commands.BucketType.user)
    @commands.command()
    async def joke(self,ctx):
        with open("Jokes/joke-fr.txt") as f:
            await ctx.message.channel.send(choice(f.readlines()).replace("\\n","\n"))
